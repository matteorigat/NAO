import os
import json
import pandas as pd
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Funzione per caricare i file JSON da una cartella
def load_json_from_folder(folder_path):
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as f:
                try:
                    file_data = json.load(f)
                    data.append(file_data)
                except json.JSONDecodeError as e:
                    print(f"Errore nel leggere il file {filename}: {e}")
    return data

# Mappiamo le emozioni di base
emotion_map = {
    "Sadness": "sad",
    "Happiness": "happy",
    "Fear": "fear",
    "Anger": "angry"
}

# Funzione per aggregare e mappare le emozioni
def process_emotion_data(files_data):
    all_data = []
    for file_data in files_data:
        for key, interactions in file_data.items():
            if key == "id":  # Ignoriamo la chiave "id"
                continue

            # Assuming interactions is a list of interaction dictionaries
            if isinstance(interactions, list):  # Add this check
                for interaction in interactions:
                    if interaction.get('interaction') == "real":
                        continue
                    # Estrazione dei dati dalla chiave
                    emotion = interaction.get('emotion')  # Use get() to avoid KeyError
                    recognized_emotion = interaction.get('emotion-recognized')  # Use get() to avoid KeyError

                    # Skip if either emotion or recognized_emotion is missing
                    if not emotion or not recognized_emotion:
                        continue

                    emotion = emotion_map[emotion.split('1')[0].split('2')[0].split('3')[0]]  # puliamo la parte numerica

                    # Aggiungiamo i dati mappati
                    all_data.append([emotion, recognized_emotion])
    return pd.DataFrame(all_data, columns=['emotion', 'emotion-recognized'])

# Caricare i dati dalla cartella
folder_path = '/Users/matteorigat/Desktop/results'  # Sostituisci con il percorso della tua cartella
files_data = load_json_from_folder(folder_path)

# Elaboriamo i dati per ottenere un DataFrame
df = process_emotion_data(files_data)

# Confrontare "emotion" con "emotion-recognized"
y_true = df["emotion"]
y_pred = df["emotion-recognized"]

# Creare la matrice di confusione
conf_matrix = confusion_matrix(y_true, y_pred, labels=['sad', 'happy', 'fear', 'angry'])

# Creare un dataframe per visualizzare la matrice di confusione
conf_matrix_df = pd.DataFrame(conf_matrix, index=['sad', 'happy', 'fear', 'angry'], columns=['sad', 'happy', 'fear', 'angry'])

# Visualizzare la matrice di confusione con un heatmap
plt.figure(figsize=(10,7))
sns.heatmap(conf_matrix_df, annot=True, fmt='d', cmap='Blues', xticklabels=['sad', 'happy', 'fear', 'angry'], yticklabels=['sad', 'happy', 'fear', 'angry'])
plt.title("Matrice di Confusione tra 'emotion' e 'emotion-recognized' aggregata da tutti i file")
plt.ylabel('Emotion (True)')
plt.xlabel('Emotion Recognized (Predicted)')
plt.show()