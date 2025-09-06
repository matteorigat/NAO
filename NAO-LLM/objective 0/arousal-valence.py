import os
import json
import pandas as pd

# --- CONFIGURAZIONE ---
# Assicurati che questo percorso sia corretto.
FOLDER_PATH = "/Users/matteorigat/Desktop/results"

# --- 1. CARICAMENTO ED ESTRAZIONE DEI DATI ---
all_ratings = []

# Controlla se la cartella specificata esiste
if not os.path.isdir(FOLDER_PATH):
    print(f"ERRORE: La cartella specificata non esiste: {FOLDER_PATH}")
else:
    # Itera su ogni file nella cartella
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith('.json'):
            file_path = os.path.join(FOLDER_PATH, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)

                # Estrai la lista delle prove (trials) dal file JSON
                trials_data = None
                for key in data.keys():
                    if key != 'id':
                        trials_data = data[key]
                        break

                # Se non ci sono dati, passa al file successivo
                if trials_data is None:
                    continue

                # Per ogni prova, estrai le informazioni necessarie
                for trial in trials_data:
                    # Ottieni la categoria di emozione base (es. 'Happiness1' -> 'Happiness')
                    emotion_category = trial['emotion'][:-1]

                    # Aggiungi i dati a una lista, convertendo valenza e arousal in numeri interi
                    all_ratings.append({
                        'emotion_category': emotion_category,
                        'valence': int(trial['valence']),
                        'arousal': int(trial['arousal'])
                    })

# --- 2. CALCOLO DELLE STATISTICHE CON PANDAS ---
if not all_ratings:
    print("ERRORE: Nessun dato è stato caricato. Controlla il percorso della cartella e il contenuto dei file.")
else:
    # Converti la lista di dizionari in un DataFrame di pandas
    df = pd.DataFrame(all_ratings)

    # Raggruppa per categoria di emozione e calcola media e deviazione standard
    # per le colonne 'valence' e 'arousal'
    results = df.groupby('emotion_category')[['valence', 'arousal']].agg(['mean', 'std'])

    # --- 3. STAMPA DEI RISULTATI ---
    print("=" * 70)
    print("Statistiche Descrittive di Valenza e Arousal per Categoria Emozionale")
    print("=" * 70)
    # Stampa il DataFrame risultante
    print(results.round(2))  # Arrotonda i risultati a 2 cifre decimali per una migliore leggibilità