import os
import json
import re
import pandas as pd
from scipy.stats import ttest_rel  # Test per campioni appaiati (related-samples)


def clean_emotion_label(label):
    """Pulisce e mappa l'etichetta dell'emozione in un formato standard."""
    label = re.sub(r'\d+', '', label).strip().lower()
    mapping = {'happiness': 'happy', 'sadness': 'sad', 'anger': 'angry', 'fear': 'fear'}
    return mapping.get(label, label)


def analyze_paired_data(directory_path):
    """
    Legge i file JSON da una directory, dove l'hash è l'ID univoco del partecipante,
    e calcola il t-test per campioni appaiati tra le condizioni 'real' e 'virtual'.
    """
    all_trials_data = []

    if not os.path.isdir(directory_path):
        print(f"Errore: La cartella '{directory_path}' non è stata trovata.")
        return

    # 1. Lettura dati, usando l'hash come ID univoco del partecipante
    print(f"Lettura dei file dalla cartella: {directory_path}\n")
    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                    # Identifica l'hash come ID del partecipante (la chiave che non è 'id')
                    participant_id = [key for key in data if key != 'id'][0]

                    trials = data[participant_id]
                    for trial in trials:
                        trial['participant_id'] = participant_id  # Associa l'hash ad ogni trial
                        all_trials_data.append(trial)
            except (json.JSONDecodeError, IndexError, KeyError) as e:
                print(f"Attenzione: Impossibile elaborare il file {filename}. Errore: {e}")

    if not all_trials_data:
        print("Nessun dato valido trovato nei file JSON.")
        return

    # 2. Creazione del DataFrame e calcolo dell'accuratezza per ogni trial
    df = pd.DataFrame(all_trials_data)
    df['valence'] = pd.to_numeric(df['valence'])
    df['arousal'] = pd.to_numeric(df['arousal'])
    df['accuracy'] = df.apply(
        lambda row: 1 if clean_emotion_label(row['emotion-recognized']) in clean_emotion_label(row['emotion']) else 0,
        axis=1
    )

    print("--- Riepilogo Dati Caricati ---")
    print(f"Numero totale di partecipanti unici (hash): {df['participant_id'].nunique()}")
    print(f"Numero totale di trial analizzati: {len(df)}")
    print("\n" + "=" * 80 + "\n")

    # 3. Aggregazione dei dati: calcolo della media per ogni partecipante in ogni condizione
    # Questo è il passaggio chiave per preparare i dati per il test appaiato
    participant_summary = df.groupby(['participant_id', 'interaction'])[['valence', 'arousal', 'accuracy']].mean()

    # Riorganizzazione della tabella (unstack) per avere le condizioni come colonne separate
    participant_summary_wide = participant_summary.unstack()

    print("--- Medie per Condizione (Statistiche Descrittive) ---")
    # Calcola le medie generali dall'aggregato per avere le medie corrette (77.8% etc.)
    print(participant_summary_wide.mean())
    print("\n" + "=" * 80 + "\n")

    # 4. Esecuzione e stampa dei T-test per Campioni Appaiati
    print("--- Risultati del T-test per Campioni Appaiati (Real vs. Virtual) ---")

    # Gradi di libertà = numero di partecipanti - 1
    degrees_of_freedom = df['participant_id'].nunique() - 1

    # Confronto sulla Valenza
    valence_ttest = ttest_rel(participant_summary_wide['valence']['real'],
                              participant_summary_wide['valence']['virtual'])
    print(f"\n1. Valenza (Valence):")
    print(
        f"   - Risultato da riportare: t({degrees_of_freedom}) = {valence_ttest.statistic:.4f}, p = {valence_ttest.pvalue:.4f}")

    # Confronto sull'Attivazione
    arousal_ttest = ttest_rel(participant_summary_wide['arousal']['real'],
                              participant_summary_wide['arousal']['virtual'])
    print(f"\n2. Attivazione (Arousal):")
    print(
        f"   - Risultato da riportare: t({degrees_of_freedom}) = {arousal_ttest.statistic:.4f}, p = {arousal_ttest.pvalue:.4f}")

    # Confronto sull'Accuratezza
    accuracy_ttest = ttest_rel(participant_summary_wide['accuracy']['real'],
                               participant_summary_wide['accuracy']['virtual'])
    print(f"\n3. Accuratezza (Accuracy):")
    print(
        f"   - Risultato da riportare: t({degrees_of_freedom}) = {accuracy_ttest.statistic:.4f}, p = {accuracy_ttest.pvalue:.4f}")

    # Interpretazione del risultato chiave
    if accuracy_ttest.pvalue < 0.05:
        print(
            "\n   - Interpretazione: La differenza nell'accuratezza tra le due condizioni È statisticamente significativa.")
    else:
        print(
            "\n   - Interpretazione: La differenza nell'accuratezza tra le due condizioni NON è statisticamente significativa.")

    print("\n" + "=" * 80 + "\n")


# --- ESECUZIONE DELLO SCRIPT ---
if __name__ == "__main__":
    # IMPORTANTE: Sostituisci questo percorso con quello corretto sul tuo computer
    results_folder_path = '/Users/matteorigat/Desktop/results'
    analyze_paired_data(results_folder_path)