import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

    plt.figure(figsize=(12, 8))

    # Only plot the means, with custom colors, larger markers, and a legend
    sns.scatterplot(x='valence', y='arousal', hue='emotion_exp', data=means, palette=emotion_colors, marker='X', s=150, legend='full')

    plt.title('Valence and Arousal of Expressed Emotions')
    plt.xlabel('Valence')
    plt.ylabel('Arousal')
    plt.xlim(1,9)
    plt.ylim(1,9)
    plt.grid(True)
     # Improve legend placement and appearance
    plt.legend(title='Emotion', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()  # Adjust layout to make room for the legend
    plt.show()

    return means #return means


# Example Usage
folder_path = "/Users/matteorigat/Desktop/results"
means_df = analyze_and_plot_emotions(folder_path)