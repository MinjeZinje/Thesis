import pandas as pd

# --- Load your raw file (change the path if needed) ---
df = pd.read_csv('summary.csv')      # expects columns: Algorithm, MeanMakespan

# --- Overall mean makespan per algorithm ---
overall = (
    df.groupby('Algorithm')['MeanMakespan']
      .mean()
      .reset_index()
      .rename(columns={'MeanMakespan': 'OverallMean'})
)

# --- Rank & Δ‑columns ---
best = overall['OverallMean'].min()
overall['Δ_units'] = overall['OverallMean'] - best
overall['Δ_pct']   = 100 * overall['Δ_units'] / best
overall = overall.sort_values('OverallMean').reset_index(drop=True)
overall.insert(0, 'Rank', overall.index + 1)

# --- Re‑order columns & show as Markdown table ---
cols = ['Rank', 'Algorithm', 'OverallMean', 'Δ_units', 'Δ_pct']
print(overall[cols].to_markdown(index=False, floatfmt='.2f'))
