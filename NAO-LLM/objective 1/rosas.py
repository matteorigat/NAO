import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- 1. Data Transcription ---
# Data remains the same as before
data = {
    'Item': [
        'Competent', 'Capable', 'Responsible', 'Interactive', 'Reliable', 'Knowledgeable',
        'Happy', 'Feeling', 'Social', 'Compassionate', 'Emotional', 'Organic',
        'Scary', 'Strange', 'Awkward', 'Dangerous', 'Awful', 'Aggressive'
    ],
    'Subscale': [
        'Competence', 'Competence', 'Competence', 'Competence', 'Competence', 'Competence',
        'Warmth', 'Warmth', 'Warmth', 'Warmth', 'Warmth', 'Warmth',
        'Discomfort', 'Discomfort', 'Discomfort', 'Discomfort', 'Discomfort', 'Discomfort'
    ],
    'P1_Real': [5, 4, 4, 5, 4, 4, 4, 3, 5, 3, 3, 3, 1, 2, 2, 1, 1, 1],
    'P2_Real': [5, 3, 4, 3, 4, 5, 5, 5, 4, 4, 5, 3, 1, 2, 2, 1, 1, 1],
    'P3_Virtual': [3, 3, 3, 3, 3, 3, 5, 5, 4, 4, 4, 3, 1, 2, 2, 1, 1, 1],
    'P4_Virtual': [4, 4, 3, 4, 3, 4, 5, 5, 5, 4, 5, 3, 1, 1, 1, 1, 1, 1]
}

df = pd.DataFrame(data)

# --- 2. Data Processing ---
# This part remains the same
df['Mean_Real'] = df[['P1_Real', 'P2_Real']].mean(axis=1)
df['Mean_Virtual'] = df[['P3_Virtual', 'P4_Virtual']].mean(axis=1)

df_melted = df.melt(
    id_vars=['Item', 'Subscale'],
    value_vars=['Mean_Real', 'Mean_Virtual'],
    var_name='Condition',
    value_name='Average Score'
)
df_melted['Condition'] = df_melted['Condition'].str.replace('Mean_', '')

# --- 3. Visualization ---
# Set the style for the plot
sns.set_theme(style="whitegrid")

# Create a faceted bar plot using catplot
g = sns.catplot(
    data=df_melted,
    x='Item',
    y='Average Score',
    hue='Condition',
    col='Subscale',
    kind='bar',
    palette={'Real': 'steelblue', 'Virtual': 'coral'},
    height=5,
    aspect=1.2,
    sharex=False
)

# --- 4. Fine-tuning Aesthetics (Larger and Bolder Text) ---

# Main figure title
#g.fig.suptitle('Mean ROSAS Scores by Condition and Subscale', fontsize=20, fontweight='bold')

# Set Y-axis properties
g.set_ylabels("Average Score", fontsize=14, fontweight='bold')
g.set(ylim=(0, 5.5))

# Iterate through each subplot (ax) to customize titles and ticks
for ax in g.axes.flat:
    # Subplot titles
    subscale_title = ax.get_title().split('=')[1].strip()
    if subscale_title in ['Competence', 'Warmth']:
        annotation_text = "(Higher is better)"
    else:
        annotation_text = "(Lower is better)"
    new_title = f'Subscale: {subscale_title}\n{annotation_text}'
    ax.set_title(new_title, fontsize=16, fontweight='bold')

    # X-axis tick labels (e.g., 'Competent', 'Capable')
    ax.tick_params(axis='x', labelrotation=45, labelsize=14)
    for label in ax.get_xticklabels():
        label.set_fontweight('bold')

    # Y-axis tick labels (the numbers 1, 2, 3, 4, 5)
    ax.tick_params(axis='y', labelsize=12)
    for label in ax.get_yticklabels():
        label.set_fontweight('bold')

    # Remove the default x-axis label ("Item")
    ax.set_xlabel('')

# Legend properties
legend = g.legend
legend.get_title().set_fontsize(14)
legend.get_title().set_fontweight('bold')
for text in legend.get_texts():
    text.set_fontsize(12)
    text.set_fontweight('bold')

# Adjust layout to prevent elements from overlapping
g.fig.tight_layout()
# Further adjust for the main title
g.fig.subplots_adjust(top=0.88)

plt.show()