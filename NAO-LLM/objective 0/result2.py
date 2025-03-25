import json
import os
import pandas as pd

emotion_map = {
    "Sadness": "sad",
    "Happiness": "happy",
    "Fear": "fear",
    "Anger": "angry"
}

def analyze_emotion_recognition(folder_path):

    all_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error reading JSON file: {filename}")  # Shorter message
                    continue

                for user_id, interactions in data.items():
                    if not isinstance(user_id, str) or user_id == "id":
                        continue
                    for interaction in interactions:
                        if interaction['interaction'] == "real": # Shorter
                            continue
                        try:
                            emotion_expressed = interaction['emotion']
                            emotion_recognized = interaction['emotion-recognized']
                            valence = float(interaction['valence'])
                            arousal = float(interaction['arousal'])

                            all_data.append({
                                'emotion_exp': emotion_expressed,  # Shorter name
                                'emotion_rec': emotion_recognized, # Shorter name
                                'valence': valence,
                                'arousal': arousal,
                                'correct': emotion_map[emotion_expressed.split('1')[0].split('2')[0].split('3')[0]].lower() == emotion_recognized.lower()
                            })
                        except KeyError as e:
                            print(f"KeyError: {e} not found in file {filename}")  # Shorter
                            continue
                        except ValueError:
                            print(f"ValueError: Invalid valence/arousal in file {filename}")  # Shorter
                            continue

    df = pd.DataFrame(all_data)

    summary = df.groupby('emotion_exp').agg(
        Correct=('correct', 'sum'),  # Shorter names
        Total=('correct', 'count'),
        Valence_Mean=('valence', 'mean'),
        Valence_Var=('valence', 'var'),
        Arousal_Mean=('arousal', 'mean'),
        Arousal_Var=('arousal', 'var')
    ).reset_index()

    summary['Incorrect'] = summary['Total'] - summary['Correct']  # Shorter
    summary['Correct_%'] = (summary['Correct'] / summary['Total'] * 100).round(1)

    def most_frequent_errors(emotion):
      errors = df[(df['emotion_exp'] == emotion) & (df['correct'] == False)]['emotion_rec']
      if errors.empty:
          return "-"
      return ", ".join([f"{emotion} ({count})" for emotion, count in errors.value_counts().items()])


    summary['Frequent_Errors'] = summary['emotion_exp'].apply(most_frequent_errors) #Shorter name
    summary = summary.sort_values(by='Correct_%', ascending=False)
    summary = summary.rename(columns={"emotion_exp": "Emotion"})  # Even shorter

    summary = summary[['Emotion', 'Correct', 'Incorrect', 'Total', 'Correct_%',
                     'Valence_Mean', 'Valence_Var', 'Arousal_Mean', 'Arousal_Var', 'Frequent_Errors']]
    summary[['Valence_Mean', 'Valence_Var', 'Arousal_Mean', 'Arousal_Var']] = summary[['Valence_Mean', 'Valence_Var', 'Arousal_Mean', 'Arousal_Var']].round(2)

    return summary


# Example usage (using the shorter folder path)
folder_path = "/Users/matteorigat/Desktop/results"
summary_table = analyze_emotion_recognition(folder_path)
print(summary_table.to_string())
# For better visualization in Jupyter:
# display(summary_table)