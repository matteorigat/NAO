import json
import os
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Mappa per normalizzare le emozioni
emotion_map = {
    "Sadness": "sad",
    "Happiness": "happy",
    "Fear": "fear",
    "Anger": "angry"
}


def normalize_emotion(emotion_str):
    """Normalizza l'emozione base, altrimenti minuscolo."""
    for base, normalized in emotion_map.items():
        if emotion_str.startswith(base):
            return normalized
    return emotion_str.lower()


def load_data(folder_path):
    """
    Carica dati da JSON, aggiungendo sia l'emozione normalizzata che quella originale.
    Ritorna DataFrame con colonne: interaction, true_emotion (norm.), true_emotion_original, recognized_emotion, valence, arousal.
    """
    records = []
    for filename in os.listdir(folder_path):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(folder_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for user_id, interactions in data.items():
                if not isinstance(interactions, list):
                    continue
                for interaction in interactions:
                    try:
                        original_emotion = interaction["emotion"]
                        records.append({
                            "interaction": interaction["interaction"],
                            "true_emotion": normalize_emotion(original_emotion),
                            "true_emotion_original": original_emotion,
                            "recognized_emotion": interaction["emotion-recognized"].lower(),
                            "valence": int(interaction["valence"]),
                            "arousal": int(interaction["arousal"])
                        })
                    except (KeyError, TypeError, ValueError):
                        # Ignora interazioni malformate
                        continue
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Errore nella lettura del file: {filename}")
            continue
    return pd.DataFrame(records)


def plot_confusion_matrix(df_subset, interaction_type, labels):
    """Calcola e mostra la confusion matrix per il sottoinsieme di dati specifico."""
    if df_subset.empty:
        print(f"Nessun dato per l'interazione '{interaction_type}'.")
        return

    cm = confusion_matrix(df_subset["true_emotion"], df_subset["recognized_emotion"], labels=labels)
    print(f"\n--- Confusion Matrix per interazione '{interaction_type}' ---")
    print(pd.DataFrame(cm, index=labels, columns=labels))

    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(cmap="Blues", xticks_rotation=45)
    plt.title(f"Confusion Matrix - {interaction_type.capitalize()}")
    plt.tight_layout()
    plt.show()


def calculate_accuracy_by_group(df, group_col):
    """
    CORRECTED & SIMPLIFIED: Calcola l'accuratezza per gruppo e per tipo di interazione.
    Ritorna un DataFrame con accuratezza per 'virtual', 'real' e 'total'.
    """
    # Aggiunge una colonna 'correct' per facilitare i calcoli
    df['correct'] = (df['true_emotion'] == df['recognized_emotion']).astype(int)

    # Calcola il numero di predizioni corrette e totali per ogni gruppo e tipo di interazione
    summary = df.groupby([group_col, 'interaction'])['correct'].agg(['sum', 'count']).unstack(fill_value=0)

    # Appiattisce i MultiIndex delle colonne (es. da ('sum', 'real') a 'sum_real')
    summary.columns = [f'{stat}_{inter}' for stat, inter in summary.columns]

    # Assicura che le colonne per entrambi i tipi di interazione esistano
    for inter in ['real', 'virtual']:
        if f'sum_{inter}' not in summary.columns:
            summary[f'sum_{inter}'] = 0
            summary[f'count_{inter}'] = 0

    # Calcola le accuratezze parziali
    summary['accuracy_virtual'] = summary['sum_virtual'] / summary['count_virtual'].replace(0, 1)
    summary['accuracy_real'] = summary['sum_real'] / summary['count_real'].replace(0, 1)

    # --- CALCOLO CORRETTO PER ACCURACY_TOTAL ---
    # Somma dei corretti (real + virtual) diviso per la somma dei totali (real + virtual)
    total_sum = summary['sum_real'] + summary['sum_virtual']
    total_count = summary['count_real'] + summary['count_virtual']
    summary['accuracy_total'] = total_sum / total_count.replace(0, 1)

    return summary[['accuracy_virtual', 'accuracy_real', 'accuracy_total']].reset_index()


def main():
    # Percorso della cartella dati
    folder_path = "/Users/matteorigat/Desktop/results"

    # Carica i dati
    df = load_data(folder_path)
    if df.empty:
        print("Nessun dato valido trovato. Verifica il percorso e il contenuto dei file JSON.")
        return

    # Aggiungi colonna "correct" per calcoli generali
    df["correct"] = df["true_emotion"] == df["recognized_emotion"]

    # Confusion matrix per tipo di interazione
    labels = sorted(df["true_emotion"].unique())
    for interaction_type in ["virtual", "real"]:
        df_subset = df[df["interaction"] == interaction_type]
        plot_confusion_matrix(df_subset, interaction_type, labels)

    # Accuracy generale per tipo di interazione
    accuracy_by_type = df.groupby("interaction")["correct"].mean()
    print("\n--- Accuratezza generale per tipo di interazione:")
    print(accuracy_by_type)

    # Accuratezza raggruppata per emozione NORMALIZZATA
    print("\n--- Accuratezza per emozione NORMALIZZATA ---")
    acc_norm = calculate_accuracy_by_group(df, "true_emotion")
    print(acc_norm.to_string())

    # Accuratezza raggruppata per emozione ORIGINALE
    print("\n--- Accuratezza per emozione ORIGINALE ---")
    acc_orig = calculate_accuracy_by_group(df, "true_emotion_original")
    print(acc_orig.to_string())


if __name__ == "__main__":
    main()