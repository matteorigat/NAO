import os
import json
import pandas as pd
from scipy.stats import mannwhitneyu

# --- CONFIGURAZIONE ---
FOLDER_PATH = "/Users/matteorigat/Desktop/results"
SIGNIFICANCE_LEVEL = 0.05

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
                        'emotion_stimulus': emotion_stimulus, 'emotion_category': true_emotion_category,
                        'accuracy': accuracy,
                    })

df = pd.DataFrame(all_trials)


# --- FUNZIONE HELPER PER ESEGUIRE E STAMPARE I TEST ---
def run_comparison(group1, group2, group1_name, group2_name):
    """Esegue un test di Mann-Whitney U e stampa i risultati in modo chiaro."""
    # Controlla se ci sono abbastanza dati in entrambi i gruppi per un confronto
    if len(group1) > 0 and len(group2) > 0:
        # Il test di Mann-Whitney U è un test per campioni indipendenti,
        # perfetto per il tuo design controbilanciato.
        stat, p_value = mannwhitneyu(group1, group2, alternative='two-sided')
        mean1 = group1.mean()
        mean2 = group2.mean()

        print(f"  - {group1_name} (Accuratezza Media: {mean1:.2%}) vs "
              f"{group2_name} (Accuratezza Media: {mean2:.2%}) "
              f"-> p-value = {p_value:.3f}", end="")

        if p_value < SIGNIFICANCE_LEVEL:
            print(" (SIGNIFICATIVO)")
        else:
            print("")
    else:
        # Questo caso si verifica se, per caso, un gesto è stato visto solo in una condizione
        print(f"  - Dati insufficienti per il confronto tra {group1_name} e {group2_name}")


# --- ESECUZIONE DELLE ANALISI A 3 LIVELLI ---

# LIVELLO 1: ANALISI GENERALE
print("=" * 70)
print("LIVELLO 1: CONFRONTO GENERALE (REAL vs VIRTUAL)")
print("=" * 70)
real_acc_total = df[df['condition'] == 'real']['accuracy']
virtual_acc_total = df[df['condition'] == 'virtual']['accuracy']
run_comparison(real_acc_total, virtual_acc_total, "Real (Totale)", "Virtual (Totale)")

# LIVELLO 2: ANALISI PER CATEGORIA EMOZIONALE
print("\n" + "=" * 70)
print("LIVELLO 2: CONFRONTO PER CATEGORIA EMOZIONALE")
print("=" * 70)
for category in sorted(df['emotion_category'].unique()):
    print(f"Categoria Emozione: {category}")
    real_cat_acc = df[(df['condition'] == 'real') & (df['emotion_category'] == category)]['accuracy']
    virtual_cat_acc = df[(df['condition'] == 'virtual') & (df['emotion_category'] == category)]['accuracy']
    run_comparison(real_cat_acc, virtual_cat_acc, "Real", "Virtual")

# LIVELLO 3: ANALISI PER SINGOLO STIMOLO (LA PIÙ PRECISA)
print("\n" + "=" * 70)
print("LIVELLO 3: CONFRONTO PER SINGOLO GESTO")
print("=" * 70)
for stimulus in sorted(df['emotion_stimulus'].unique()):
    print(f"Gesto Specifico: {stimulus}")
    real_stim_acc = df[(df['condition'] == 'real') & (df['emotion_stimulus'] == stimulus)]['accuracy']
    virtual_stim_acc = df[(df['condition'] == 'virtual') & (df['emotion_stimulus'] == stimulus)]['accuracy']
    run_comparison(real_stim_acc, virtual_stim_acc, "Real", "Virtual")