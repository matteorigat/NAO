import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re

from matplotlib.lines import Line2D

# This map translates the base emotion category to the expected recognized label.
emotion_map = {
    "Sadness": "sad",
    "Happiness": "happy",
    "Fear": "fear",
    "Anger": "angry"
}


def analyze_and_plot_emotion_averages(folder_path):
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
                        try:
                            emotion_expressed = interaction['emotion']
                            emotion_recognized = interaction['emotion-recognized']
                            valence = float(interaction['valence'])
                            arousal = float(interaction['arousal'])

                            base_emotion_match = re.match(r'([A-Za-z]+)', emotion_expressed)
                            if not base_emotion_match:
                                print(f"Could not parse base emotion from '{emotion_expressed}' in {filename}. Skipping.")
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
        print("No valid data found in the specified folder.")
        return None

    df = pd.DataFrame(all_data)
    means_df = df.groupby(['emotion_exp', 'successful'])[['valence', 'arousal']].mean().reset_index()

    print("\nCalculated Averages for Plotting:")
    print(means_df)

    emotion_colors = {
        'Happiness1': '#CCCC33',  # Yellow
        'Happiness3': '#E6E600',
        'Happiness2': '#FFFF99',  # l
        'Fear1': '#228B22',  # Green
        'Fear2': '#32CD32',
        'Fear3': '#99FF99',  # l
        'Anger3': '#800000',  # red
        'Anger1': '#CC0000',
        'Anger2': '#FF9999',  # l
        'Sadness1': '#000080',  # blue
        'Sadness3': '#6495ED',
        'Sadness2': '#A6C8FF',  # l
    }

    plt.figure(figsize=(14, 10))

    ax = sns.scatterplot(
        data=means_df,
        x='valence',
        y='arousal',
        hue='emotion_exp',
        style='successful',
        palette=emotion_colors,
        markers={True: 'o', False: 'X'},
        s=250,
        alpha=0.9,
        edgecolor='black',
        linewidth=1.5
    )

    # --- Plot Decorations (Russell's Circumplex Model) ---
    plt.title('Average Valence & Arousal - Real and virtual combined', fontsize=20, pad=20)
    plt.xlabel('Valence', fontsize=18)
    plt.ylabel('Arousal', fontsize=18)
    plt.xlim(0.5, 9.5)
    plt.ylim(0.5, 9.5)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.grid(True, linestyle=':', alpha=0.6)

    plt.axhline(y=5, color='black', linestyle='-', linewidth=1.5)
    plt.axvline(x=5, color='black', linestyle='-', linewidth=1.5)

    circle = plt.Circle((5, 5), radius=4, color='gray', fill=False, linestyle='--', linewidth=1.5)
    ax.add_patch(circle)

    # Quadrant labels for context
    label_positions = {
        'High Arousal': (5, 9.3, 'center', 'top'),
        'Low Arousal': (5, 0.7, 'center', 'bottom'),
        'Pleasant': (9.4, 5.2, 'right', 'center'),
        'Unpleasant': (0.6, 5.2, 'left', 'center'),
        'Fear': (1.5, 7.5, 'center', 'center'),
        'Anger': (1.0, 6.8, 'center', 'center'),
        'Happiness': (8.9, 6.0, 'center', 'center'),
        'Sadness': (1.0, 3.5, 'center', 'center')
    }
    # This loop now correctly iterates through ALL labels and adds them to the plot
    for label, (x, y, ha, va) in label_positions.items():
        plt.text(x, y, label, fontsize=16, ha=ha, va=va, fontweight='bold', alpha=0.7, color='gray')

    # <<< START: THIS ENTIRE BLOCK WAS MOVED OUT OF THE LOOP ABOVE >>>

    # --- BUILD THE LEGEND MANUALLY ---
    # 1. Emotion labels (using the order from the colors dictionary for consistency)
    emotion_labels_ordered = list(emotion_colors.keys())
    emotion_legend = [
        Line2D([0], [0],
               marker='o',
               color='w', # Hide the line
               label=emotion,
               markerfacecolor=emotion_colors[emotion],
               markeredgecolor='black',
               markersize=16)
        for emotion in emotion_labels_ordered
    ]

    # 2. Success/Failure marker labels
    success_legend = [
        Line2D([0], [0], marker='', color='w', label='', # Blank space for separation
               markerfacecolor='black', markersize=16),
        Line2D([0], [0], marker='o', color='w', label='Success (Avg)',
               markerfacecolor='dimgray', markeredgecolor='black', markersize=16),
        Line2D([0], [0], marker='X', color='w', label='Failure (Avg)',
               markerfacecolor='dimgray', markeredgecolor='black', markersize=16)
    ]

    # 3. Combine legend parts and display
    custom_legend = emotion_legend + success_legend

    ax.legend(
        handles=custom_legend,
        # labels=[h.get_label() for h in custom_legend], # Not needed when using handles
        title='Emotion & Recognition',
        title_fontsize=16,
        fontsize=14,
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        borderaxespad=0.,
        labelspacing=1.2
    )

    ax.set_aspect('equal', adjustable='datalim')

    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust layout for the legend
    plt.show()

    # <<< END: END OF THE MOVED BLOCK >>>

    return means_df


# --- Example Usage ---
# IMPORTANT: Replace this path with the actual path to your results folder.
folder_path = "/Users/matteorigat/Desktop/results"
avg_results_df = analyze_and_plot_emotion_averages(folder_path)