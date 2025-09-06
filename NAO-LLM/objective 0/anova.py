import os
import json
import pandas as pd
import pingouin as pg
from statsmodels.stats.anova import AnovaRM

# --- CONFIGURAZIONE ---
FOLDER_PATH = "/Users/matteorigat/Desktop/results"
SIGNIFICANCE_LEVEL = 0.05

# --- NUOVA IMPOSTAZIONE PANDAS ---
# Assicura che pandas stampi tutte le colonne del DataFrame, senza troncarle.
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000) # Aumenta la larghezza per evitare che le righe vadano a capo

# Mapping per standardizzare i nomi delle emozioni
EMOTION_MAPPING = {
    'happy': 'Happiness', 'sad': 'Sadness', 'angry': 'Anger', 'fear': 'Fear'
}

# --- 1. CARICAMENTO E PRE-ELABORAZIONE DEI DATI ---
all_trials = []
if not os.path.isdir(FOLDER_PATH):
    print(f"ERRORE: La cartella specificata non esiste: {FOLDER_PATH}")
else:
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith('.json'):
            file_path = os.path.join(FOLDER_PATH, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
                participant_id, trials_data = None, None
                for key in data.keys():
                    if key != 'id':
                        participant_id, trials_data = key, data[key]
                        break
                if trials_data is None: continue
                for trial in trials_data:
                    emotion_stimulus = trial['emotion']
                    true_emotion_category = emotion_stimulus[:-1]
                    recognized_emotion = EMOTION_MAPPING.get(trial['emotion-recognized'], 'Other')
                    accuracy = 1 if true_emotion_category == recognized_emotion else 0
                    all_trials.append({
                        'participant_id': participant_id, 'condition': trial['interaction'],
                        'emotion_category': true_emotion_category, 'accuracy': accuracy,
                    })

df = pd.DataFrame(all_trials)

if df.empty:
    print("ERRORE: Nessun dato è stato caricato.")
else:
    # --- 2. PREPARAZIONE DATI PER ANOVA 2x4 ---
    df_agg = df.groupby(['participant_id', 'condition', 'emotion_category'])['accuracy'].mean().reset_index()

    print("=" * 70)
    print("ANALISI CON ANOVA A MISURE RIPETUTE (2x4)")
    print("=" * 70)

    # --- 3. ESECUZIONE DELL'ANOVA ---
    print("\n--- Risultati del Test ANOVA Complessivo ---")
    try:
        aov = AnovaRM(data=df_agg, depvar='accuracy', subject='participant_id',
                      within=['condition', 'emotion_category'])
        res = aov.fit()
        print(res)
    except Exception as e:
        print(f"Errore ANOVA: {e}")

    # --- 4. ESECUZIONE DEI TEST POST-HOC ---
    print("\n" + "=" * 70)
    print("ANALISI POST-HOC (Confronti a Coppie Dettagliati)")
    print("=" * 70)

    print("\n--- A) Post-hoc per l'Effetto Principale di EMOZIONE ---")
    print("Confronta ogni categoria emozionale con le altre, mediando tra Real e Virtual.")
    try:
        posthoc_emotion = pg.pairwise_tests(data=df_agg, dv='accuracy', within='emotion_category',
                                            subject='participant_id', padjust='bonf')
        # MODIFICA: Rimuoviamo la selezione delle colonne per stampare l'intero DataFrame
        print(posthoc_emotion)
    except Exception as e:
        print(f"Errore Post-hoc Emozione: {e}")

    print("\n\n--- B) Post-hoc per l'Effetto Principale di CONDIZIONE ---")
    print("Confronta Real vs. Virtual, mediando tra tutte le emozioni.")
    try:
        posthoc_condition = pg.pairwise_tests(data=df_agg, dv='accuracy', within='condition', subject='participant_id',
                                              padjust='bonf')
        # MODIFICA: Rimuoviamo la selezione delle colonne per stampare l'intero DataFrame
        print(posthoc_condition)
    except Exception as e:
        print(f"Errore Post-hoc Condizione: {e}")

    print("\n\n--- C) Post-hoc per l'INTERAZIONE (il test più interessante) ---")
    print("Confronta Real vs. Virtual all'interno di ogni singola categoria emozionale.")
    try:
        for emotion in sorted(df_agg['emotion_category'].unique()):
            print(f"\nCategoria Emozione: {emotion}")
            emotion_df = df_agg[df_agg['emotion_category'] == emotion]

            posthoc_inter = pg.pairwise_tests(
                data=emotion_df,
                dv='accuracy',
                within='condition',
                subject='participant_id',
                padjust='bonf'
            )
            # MODIFICA: Rimuoviamo la selezione delle colonne per stampare l'intero DataFrame
            print(posthoc_inter)
    except Exception as e:
        print(f"Errore Post-hoc Interazione: {e}")