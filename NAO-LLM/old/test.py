import json
import os
from collections import Counter
import random # Needed for tie-breaking

def get_least_frequent_six(gesture_counts: Counter):
    """
    Selects the 6 least frequent gestures from a Counter object.
    Handles ties by random selection.

    Args:
        gesture_counts (Counter): A Counter mapping gestures to their frequencies.

    Returns:
        list: A list containing exactly 6 gestures, representing the least frequent ones.
              Returns fewer if less than 6 unique gestures exist.
    """
    if not gesture_counts:
        return []

    # Sort gestures by count (ascending), then alphabetically for consistent tie-breaking before random sampling
    sorted_gestures = sorted(gesture_counts.items(), key=lambda item: (item[1], item[0]))

    # If 6 or fewer unique gestures exist, return all of them
    if len(sorted_gestures) <= 6:
        return [gesture for gesture, count in sorted_gestures]

    # Determine the count of the 6th least frequent gesture
    cutoff_count = sorted_gestures[5][1]

    # Get all gestures with counts strictly less than the cutoff
    strictly_less = [g for g, count in sorted_gestures if count < cutoff_count]

    # Get all gestures with counts exactly equal to the cutoff (potential ties)
    tied_for_cutoff = [g for g, count in sorted_gestures if count == cutoff_count]

    # How many more gestures do we need to reach 6?
    needed = 6 - len(strictly_less)

    # Randomly select 'needed' gestures from the tied group
    # Ensure sample size isn't larger than population
    if needed > 0:
        chosen_from_tied = random.sample(tied_for_cutoff, min(needed, len(tied_for_cutoff)))
    else:
        chosen_from_tied = [] # Should not happen if logic is right, but safe check

    # Combine the lists
    final_list = strictly_less + chosen_from_tied

    # Shuffle the final list for random order among the selected 6
    random.shuffle(final_list)

    return final_list


def analyze_interactions_for_least_frequent(folder_path):
    """
    Analyzes JSON files to count interaction starts and find the 6 least
    frequent gestures per condition (virtual/real).

    Args:
        folder_path (str): The path to the folder containing JSON files.

    Returns:
        tuple: Contains virtual_starts, real_starts, least_freq_virtual_6, least_freq_real_6
    """
    virtual_starts = 0
    real_starts = 0
    virtual_gesture_counts = Counter()
    real_gesture_counts = Counter()
    processed_files = 0
    skipped_files = 0

    print(f"Analyzing files in: {folder_path}")
    # --- File Iteration and Counting (same as before) ---
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
                        gesture = interaction.get('emotion') # Using 'emotion' key for gesture name
                        if condition and gesture:
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

    # --- Selection of 6 Least Frequent ---
    least_freq_virtual_6 = get_least_frequent_six(virtual_gesture_counts)
    least_freq_real_6 = get_least_frequent_six(real_gesture_counts)

    # --- Optional: Print counts for verification ---
    # print("\nVirtual Gesture Counts:")
    # print(dict(virtual_gesture_counts.most_common())) # Print all counts sorted high to low
    # print("\nReal Gesture Counts:")
    # print(dict(real_gesture_counts.most_common()))

    return (virtual_starts, real_starts, least_freq_virtual_6, least_freq_real_6)

# === Example Usage ===
folder_path = "/Users/matteorigat/Desktop/results" # Use your actual path

if os.path.exists(folder_path):
    (v_starts, r_starts, least_v_6, least_r_6) = \
        analyze_interactions_for_least_frequent(folder_path)

    print("-" * 30)
    print("Session Start Counts:")
    print(f"Started with Virtual: {v_starts}")
    print(f"Started with Real:    {r_starts}")
    print(f"Total Sessions Analyzed: {v_starts + r_starts}")
    print("-" * 30)

    print("6 Least Frequent Gestures Shown (Random tie-breaking):")
    print("gestures_list = [")
    print(f"    # Virtual list (index 0)")
    # Ensure output is a valid list string even if empty or less than 6
    print(f"    {least_v_6},")
    print(f"    # Real list (index 1)")
    print(f"    {least_r_6}")
    print("]")
    print("-" * 30)

else:
    print(f"Error: Folder not found at {folder_path}")