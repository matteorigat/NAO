import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

emotion_map = {
    "Sadness": "sad",
    "Happiness": "happy",
    "Fear": "fear",
    "Anger": "angry"
}

def analyze_and_plot_emotions(folder_path):

    all_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error reading JSON file: {filename}")
                    continue

                for user_id, interactions in data.items():
                    if not isinstance(user_id, str) or user_id == "id":
                        continue
                    for interaction in interactions:
                        if interaction['interaction'] == "virtual":
                            continue
                        try:
                            emotion_expressed = interaction['emotion']
                            valence = float(interaction['valence'])
                            arousal = float(interaction['arousal'])

                            all_data.append({
                                'emotion_exp': emotion_expressed,
                                'valence': valence,
                                'arousal': arousal,
                            })
                        except KeyError as e:
                            print(f"KeyError: {e} not found in file {filename}")
                            continue
                        except ValueError:
                            print(f"ValueError: Invalid valence/arousal in file {filename}")
                            continue

    df = pd.DataFrame(all_data)

    # Define a more consistent color palette
    emotion_colors = {
        'Anger1': '#800000',       # red
        'Anger2': '#FF9999',#l
        'Anger3': '#CC0000',
        'Happiness1': '#CCCC33',   # Yellow
        'Happiness2': '#FFFF99', #l
        'Happiness3': '#E6E600',
        'Fear1': '#228B22',        # Green
        'Fear2': '#32CD32',
        'Fear3': '#99FF99', #l
        'Sadness1': '#000080',     # blue
        'Sadness2': '#A6C8FF', #l
        'Sadness3': '#6495ED',
    }
     # Add a 'color' column to the DataFrame, handling missing emotions
    df['color'] = df['emotion_exp'].map(emotion_colors)
    missing_colors = df['color'].isnull()
    if missing_colors.any():
        print("Warning: Some emotions are missing from the color palette:")
        print(df.loc[missing_colors, 'emotion_exp'].unique())
        # Don't set a default in this case, just warn.  Let the legend handle it.

    means = df.groupby('emotion_exp')[['valence', 'arousal']].mean().reset_index()
    means['color'] = means['emotion_exp'].map(emotion_colors)

    plt.figure(figsize=(12, 10))

    # Only plot the means, with custom colors, larger markers, and a legend
    sns.scatterplot(x='valence', y='arousal', hue='emotion_exp', data=means, palette=emotion_colors, marker='X', s=150, legend='full')

    # Etichette e layout
    plt.title('Valence and Arousal of Expressed Emotions')
    plt.xlabel('Valence')
    plt.ylabel('Arousal')
    plt.xlim(1, 9)
    plt.ylim(1, 9)
    plt.grid(True)
    plt.axhline(y=5, color='gray', linestyle='-', linewidth=2)
    plt.axvline(x=5, color='gray', linestyle='-', linewidth=2)
    plt.legend(title='Emotion', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Aggiunta della circonferenza
    circle = plt.Circle((5, 5), radius=4, color='gray', fill=False, linestyle='--', linewidth=1.5)
    plt.gca().add_patch(circle)

    # Posizionamento delle etichette sulla circonferenza
    label_positions = {
        'Happiness': 10,
        'Fear': 135,
        'Anger': 155,
        'Sadness': 200
    }

    for label, angle_deg in label_positions.items():
        angle_rad = np.deg2rad(angle_deg)
        x = 5 + 4.2 * np.cos(angle_rad)  # 4.2 to slightly push text outside the circle
        y = 5 + 4.2 * np.sin(angle_rad)
        ha = 'center'
        va = 'center'
        if 45 < angle_deg < 135:
            va = 'bottom'
        elif 225 < angle_deg < 315:
            va = 'top'
        elif angle_deg < 45 or angle_deg > 315:
            ha = 'left'
        elif 135 < angle_deg < 225:
            ha = 'right'

        plt.text(x, y, label, fontsize=12, ha=ha, va=va, fontweight='bold')

    plt.tight_layout()
    plt.show()
    return means #return means


# Example Usage
folder_path = "/Users/matteorigat/Desktop/results"
means_df = analyze_and_plot_emotions(folder_path)



"""

 # Plot dei sottogruppi
    sns.scatterplot(
        x='valence', y='arousal', hue='emotion_exp',
        data=means, palette=emotion_colors, marker='X', s=150, legend='full'
    )

    # Calcolo medie per le 4 emozioni principali
    emotion_core_means = []
    for core_emotion in ['Happiness', 'Sadness', 'Anger', 'Fear']:
        matching_rows = means[means['emotion_exp'].str.startswith(core_emotion)]
        if not matching_rows.empty:
            avg_val = matching_rows['valence'].mean()
            avg_ar = matching_rows['arousal'].mean()
            emotion_core_means.append({
                'emotion': core_emotion,
                'valence': avg_val,
                'arousal': avg_ar
            })

    # Colori distintivi per le emozioni principali (più scuri o neutri)
    core_colors = {
        'Happiness': '#999900',
        'Sadness': '#0000CC',
        'Anger': '#990000',
        'Fear': '#006600'
    }

    # Aggiunta dei punti medi delle emozioni principali
    for item in emotion_core_means:
        plt.scatter(item['valence'], item['arousal'],
                    s=300, c=core_colors[item['emotion']],
                    marker='o', edgecolors='black', linewidths=1.5,
                    label=f"{item['emotion']} (avg)")

    # Etichette e layout
    plt.title('Valence and Arousal of Expressed Emotions')
    plt.xlabel('Valence')
    plt.ylabel('Arousal')
    plt.xlim(1, 9)
    plt.ylim(1, 9)
    plt.grid(True)
    plt.legend(title='Emotion', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()


"""