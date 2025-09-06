import os
import json
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import re

def load_json_from_folder(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                    data.append(file_data)
            except json.JSONDecodeError as e:
                print(f"Errore nel leggere il file {filename}: {e}")
    return data

def clean_emotion_label(label):
    # Pulisce e mappa l'etichetta in formato standard
    label = re.sub(r'\d+', '', label).strip().lower()
    mapping = {
        'happiness': 'happy',
        'sadness': 'sad',
        'anger': 'angry',
        'fear': 'fear'
    }
    return mapping.get(label, label)

def process_emotion_data(files_data):
    all_data = []
    for file_data in files_data:
        for key, interactions in file_data.items():
            if key == "id" or not isinstance(interactions, list):
                continue
            for interaction in interactions:
                if interaction.get("interaction") != "virtual":
                    continue
                true_emotion = interaction.get('emotion')
                recognized_emotion = interaction.get('emotion-recognized')
                if not true_emotion or not recognized_emotion:
                    continue
                true_clean = clean_emotion_label(true_emotion)
                recognized_clean = clean_emotion_label(recognized_emotion)
                all_data.append([true_clean, recognized_clean])
    return pd.DataFrame(all_data, columns=['emotion', 'emotion-recognized'])

def plot_confusion_matrix(df, internal_labels, display_labels):
    y_true = df["emotion"]
    y_pred = df["emotion-recognized"]

    matrix = confusion_matrix(y_true, y_pred, labels=internal_labels)
    matrix_df = pd.DataFrame(matrix, index=display_labels, columns=display_labels)

    plt.figure(figsize=(8, 8))
    ax = sns.heatmap(matrix_df, annot=True, fmt='d', cmap='Blues', cbar=False,
                     annot_kws={"size": 16})
    ax.set_title("Virtual", fontsize=20)
    ax.set_xlabel("Emotion Recognized (Predicted)", fontsize=16)
    ax.set_ylabel("Emotion (True)", fontsize=16)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    plt.tight_layout()
    plt.show()

# === ESECUZIONE ===
folder_path = '/Users/matteorigat/Desktop/results'
files_data = load_json_from_folder(folder_path)
df = process_emotion_data(files_data)

# Etichette per i dati (interni) e per la visualizzazione
internal_labels = ['happy', 'sad', 'angry', 'fear']
display_labels = ['Happiness', 'Sadness', 'Anger', 'Fear']

plot_confusion_matrix(df, internal_labels, display_labels)