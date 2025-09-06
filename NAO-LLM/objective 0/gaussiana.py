import os
import json
import re
import pandas as pd
from scipy.stats import shapiro
import matplotlib.pyplot as plt
import statsmodels.api as sm


def clean_emotion_label(label):
    label = re.sub(r'\d+', '', label).strip().lower()
    mapping = {'happiness': 'happy', 'sadness': 'sad', 'anger': 'angry', 'fear': 'fear'}
    return mapping.get(label, label)


def extract_accuracies(directory_path):
    all_trials = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            with open(os.path.join(directory_path, filename), 'r') as f:
                data = json.load(f)
                participant_id = [k for k in data if k != "id"][0]
                trials = data[participant_id]
                for trial in trials:
                    trial['participant_id'] = participant_id
                    all_trials.append(trial)

    df = pd.DataFrame(all_trials)
    df['accuracy'] = df.apply(
        lambda row: 1 if clean_emotion_label(row['emotion-recognized']) in clean_emotion_label(row['emotion']) else 0,
        axis=1
    )

    # Media accuracy per partecipante e condizione
    summary = df.groupby(['participant_id', 'interaction'])['accuracy'].mean().unstack()
    return summary.dropna()  # Elimina partecipanti con dati incompleti


def analyze_normality(summary_df):
    diff = summary_df['real'] - summary_df['virtual']
    stat, p = shapiro(diff)

    print("\n--- Shapiro-Wilk Test ---")
    print(f"Statistic: {stat:.4f}, p-value: {p:.4f}")
    if p > 0.05:
        print("✅ Le differenze seguono una distribuzione normale.")
    else:
        print("❌ Le differenze NON seguono una distribuzione normale.")

    # Plot istogramma e Q-Q plot
    plt.figure()
    plt.hist(diff, bins=10, edgecolor='black')
    plt.title("Istogramma delle Differenze (Real - Virtual)")
    plt.xlabel("Differenza di Accuratezza")
    plt.ylabel("Frequenza")
    plt.show()

    sm.qqplot(diff, line='s')
    plt.title("Q-Q Plot delle Differenze")
    plt.show()


# --- Esecuzione ---
if __name__ == "__main__":
    folder = "/Users/matteorigat/Desktop/results"
    summary = extract_accuracies(folder)
    analyze_normality(summary)
