import json
import os
from collections import Counter
import random # Still needed for shuffling final lists if desired

# Define the expected full set of 12 gestures
ALL_EXPECTED_GESTURES = {
    "Happiness1", "Happiness2", "Happiness3",
    "Sadness1", "Sadness2", "Sadness3",
    "Anger1", "Anger2", "Anger3",
    "Fear1", "Fear2", "Fear3"
}

def analyze_and_partition_gestures(folder_path):
    """
    Analyzes JSON files to count interaction starts and partition the 12
    unique gestures into two lists of 6 based on relative frequency
    in virtual vs. real conditions.

    Args:
        folder_path (str): The path to the folder containing JSON files.

    Returns:
        tuple: Contains virtual_starts, real_starts, least_freq_virtual_partition, least_freq_real_partition
    """
    virtual_starts = 0
    real_starts = 0
    virtual_gesture_counts = Counter()
    real_gesture_counts = Counter()
    processed_files = 0
    skipped_files = 0
    observed_gestures = set()

    print(f"Analyzing files in: {folder_path}")
    # --- File Iteration and Counting ---
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                interactions = None
                for key, value in data.items():
                    if key.lower() != "id" and isinstance(value, list):
                       interactions = value
                       break

                if interactions is None:
                    skipped_files += 1
                    continue

                if interactions:
                    first_interaction = interactions[0]
                    if isinstance(first_interaction, dict):
                        start_condition = first_interaction.get('interaction')
                        if start_condition == 'virtual':
                            virtual_starts += 1
                        elif start_condition == 'real':
                            real_starts += 1

                for interaction in interactions:
                    if isinstance(interaction, dict):
                        condition = interaction.get('interaction')
                        gesture = interaction.get('emotion') # Using 'emotion' key
                        if condition and gesture:
                            observed_gestures.add(gesture) # Track observed gestures
                            if condition == 'virtual':
                                virtual_gesture_counts[gesture] += 1
                            elif condition == 'real':
                                real_gesture_counts[gesture] += 1
                processed_files += 1

            except json.JSONDecodeError:
                print(f"Skipping {filename}: Invalid JSON format.")
                skipped_files += 1
            except Exception as e:
                print(f"Skipping {filename}: Error during processing - {e}")
                skipped_files += 1

    print(f"\nProcessed {processed_files} files, skipped {skipped_files} files.")
    print(f"Observed {len(observed_gestures)} unique gestures.")

    # --- Partitioning Logic ---
    gesture_scores = []
    # Use ALL_EXPECTED_GESTURES to ensure all 12 are considered, even if count is 0
    for gesture in ALL_EXPECTED_GESTURES:
        v_count = virtual_gesture_counts.get(gesture, 0)
        r_count = real_gesture_counts.get(gesture, 0)

        # Score: Higher score means relatively less frequent in VIRTUAL
        #        Lower score means relatively less frequent in REAL
        # Using difference: r_count - v_count
        # Add a small bias based on total counts if difference is 0? Optional.
        score = r_count - v_count

        # Add total count as secondary sort key for tie-breaking (less frequent overall gets higher priority)
        # And gesture name as tertiary for deterministic sort
        total_count = v_count + r_count
        gesture_scores.append((score, total_count, gesture))

    # Sort by score (ascending). Gestures least frequent in REAL (more frequent in virtual) will be first.
    # Then by total_count (ascending) - fewer appearances overall ranked higher for "least frequent"
    # Then by gesture name (ascending) for stability
    gesture_scores.sort(key=lambda x: (x[0], x[1], x[2]))

    # The first 6 are assigned to the "least frequent in real" list
    # The last 6 are assigned to the "least frequent in virtual" list
    if len(gesture_scores) != 12:
        print(f"Warning: Expected 12 unique gestures, but found/scored {len(gesture_scores)}. Results might be incomplete.")
        # Handle gracefully, maybe pad lists or just return what was found?
        # For now, just take the available ones

    # Extract gesture names from the sorted list
    sorted_gestures_only = [g for score, total_c, g in gesture_scores]

    least_freq_real_partition = sorted_gestures_only[:6]
    least_freq_virtual_partition = sorted_gestures_only[6:] # Takes from index 6 to the end

    # Optional: Shuffle the final lists if the order within the 6 doesn't matter
    random.shuffle(least_freq_virtual_partition)
    random.shuffle(least_freq_real_partition)

    return (virtual_starts, real_starts, least_freq_virtual_partition, least_freq_real_partition)

# === Example Usage ===
folder_path = "/Users/matteorigat/Desktop/results" # Use your actual path

if os.path.exists(folder_path):
    (v_starts, r_starts, least_v_part, least_r_part) = \
        analyze_and_partition_gestures(folder_path)

    print("-" * 30)
    print("Session Start Counts:")
    print(f"Started with Virtual: {v_starts}")
    print(f"Started with Real:    {r_starts}")
    print(f"Total Sessions Analyzed: {v_starts + r_starts}")
    print("-" * 30)

    print("Partitioned Gestures (6 unique per list based on relative frequency):")
    print("gestures_list = [")
    print(f"    # Virtual list (Gestures relatively less frequent here)")
    print(f"    {least_v_part},")
    print(f"    # Real list (Gestures relatively less frequent here)")
    print(f"    {least_r_part}")
    print("]")
    print("-" * 30)

else:
    print(f"Error: Folder not found at {folder_path}")