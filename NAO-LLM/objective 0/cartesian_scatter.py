import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

# This map translates the base emotion category to the expected recognized label.
emotion_map = {
    "Sadness": "sad",
    "Happiness": "happy",
    "Fear": "fear",
    "Anger": "angry"
}


def analyze_and_plot_individual_emotions(folder_path):
    """
    Analyzes individual emotion interaction data from JSON files.

    To accurately visualize the distribution of discrete integer ratings without
    overplotting, this function plots every individual data point using:
    1. Jitter: Adds small random noise to each point's position.
    2. Transparency (Alpha): Makes points semi-transparent so dense areas appear darker.

    - A point ('o') marker represents a successful recognition.
    - An 'X' marker represents an unsuccessful recognition.
    """
    all_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error reading JSON file (skipping): {filename}")
                    continue

                for user_id, interactions in data.items():
                    if not isinstance(interactions, list):
                        continue

                    for interaction in interactions:
                        #if interaction.get('interaction') != "real":
                        #    continue

                        try:
                            emotion_expressed = interaction['emotion']
                            emotion_recognized = interaction['emotion-recognized']
                            valence = float(interaction['valence'])
                            arousal = float(interaction['arousal'])

                            base_emotion_match = re.match(r'([A-Za-z]+)', emotion_expressed)
                            if not base_emotion_match:
                                print(
                                    f"Could not parse base emotion from '{emotion_expressed}' in {filename}. Skipping.")
                                continue

                            base_emotion = base_emotion_match.group(1)
                            expected_recognition = emotion_map.get(base_emotion)
                            is_successful = (expected_recognition == emotion_recognized)

                            all_data.append({
                                'emotion_exp': emotion_expressed,
                                'valence': valence,
                                'arousal': arousal,
                                'successful': is_successful,
                            })
                        except (KeyError, AttributeError, ValueError) as e:
                            print(f"Skipping malformed record in {filename}: {e}")
                            continue

    if not all_data:
        print("No valid 'real' interaction data found in the specified folder.")
        return None

    # --- PLOTTING INDIVIDUAL POINTS: NO AVERAGING ---
    df = pd.DataFrame(all_data)

    # --- JITTER IMPLEMENTATION ---
    # Add small random noise to valence and arousal for visualization
    # The amount of jitter (0.25) is chosen to spread points without distorting the grid.
    jitter_strength = 0.15
    df['valence_jitter'] = df['valence'] + np.random.uniform(-jitter_strength, jitter_strength, size=len(df))
    df['arousal_jitter'] = df['arousal'] + np.random.uniform(-jitter_strength, jitter_strength, size=len(df))

    emotion_colors = {
        'Anger1': '#800000',
        'Anger2': '#FF9999',
        'Anger3': '#CC0000',
        'Happiness1': '#CCCC33',
        'Happiness2': '#FFFF99',
        'Happiness3': '#E6E600',
        'Fear1': '#228B22',
        'Fear2': '#32CD32',
        'Fear3': '#99FF99',
        'Sadness1': '#000080',
        'Sadness2': '#A6C8FF',
        'Sadness3': '#6495ED',
    }

    plt.figure(figsize=(14, 10))

    # --- PLOT THE JITTERED, TRANSPARENT POINTS ---
    ax = sns.scatterplot(
        data=df,
        x='valence_jitter',  # Use jittered data for plotting
        y='arousal_jitter',  # Use jittered data for plotting
        hue='emotion_exp',
        style='successful',
        palette=emotion_colors,
        markers={True: 'o', False: 'X'},
        s=70,  # Smaller markers suitable for many points
        alpha=0.6,  # Key for seeing density
        edgecolor='black',
        linewidth=0.5
    )

    # --- Plot Decorations (Russell's Circumplex Model) ---
    plt.title('Individual Valence & Arousal Ratings by Recognition Success (with Jitter)', fontsize=16, pad=20)
    plt.xlabel('Valence (1=Negative, 9=Positive)', fontsize=12)
    plt.ylabel('Arousal (1=Low, 9=High)', fontsize=12)
    plt.xlim(0.5, 9.5)
    plt.ylim(0.5, 9.5)

    # Set grid lines to correspond to the original integer values
    plt.xticks(np.arange(1, 10, 1))
    plt.yticks(np.arange(1, 10, 1))
    plt.grid(True, linestyle=':', alpha=0.6)

    plt.axhline(y=5, color='black', linestyle='-', linewidth=1.5)
    plt.axvline(x=5, color='black', linestyle='-', linewidth=1.5)

    circle = plt.Circle((5, 5), radius=4, color='gray', fill=False, linestyle='--', linewidth=1.5)
    ax.add_patch(circle)

    label_positions = {
        'High Arousal': (5, 9.2, 'center', 'top'),
        'Low Arousal': (5, 0.8, 'center', 'bottom'),
        'Pleasant': (9.4, 5.1, 'right', 'center'),
        'Unpleasant': (0.6, 5.1, 'left', 'center'),
    }
    for label, (x, y, ha, va) in label_positions.items():
        plt.text(x, y, label, fontsize=12, ha=ha, va=va, fontweight='bold', alpha=0.7, color='gray')

    # Update legend to remove "(Avg)" from labels
    handles, labels = ax.get_legend_handles_labels()
    filtered = [(h, l) for h, l in zip(handles, labels) if l != 'emotion_exp']
    handles, labels = zip(*filtered)
    handles = list(handles)
    labels = list(labels)

    try:
        style_start_index = labels.index('successful')
        labels[style_start_index] = '\nRecognition Status'
        labels[style_start_index + 1] = 'Success'
        labels[style_start_index + 2] = 'Failure'
    except ValueError:
        print("Could not automatically relabel legend.")

    ax.legend(handles, labels, title='Emotion', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.,
              labelspacing=1.2)

    plt.tight_layout(rect=[0, 0, 0.85, 1])
    plt.show()

    # Return the original dataframe without the jitter columns for further analysis
    return df.drop(columns=['valence_jitter', 'arousal_jitter'])


# --- Example Usage ---
# IMPORTANT: Replace this path with the actual path to your results folder.
folder_path = "/Users/matteorigat/Desktop/results"
full_df = analyze_and_plot_individual_emotions(folder_path)
if full_df is not None:
    print("\nSample of the full dataset:")
    print(full_df.head())