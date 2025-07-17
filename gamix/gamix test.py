import pandas as pd
from scipy import stats
import itertools

df = pd.read_csv('summary.csv')     # must have Instance, Scenario, Algorithm, Makespan
pivot = df.pivot_table(values='Makespan',
                       index=['Instance', 'Scenario'],
                       columns='Algorithm')

# Drop any rows with missing values
pivot = pivot.dropna()

# ---------- Friedman test (non‑parametric ANOVA) ----------
stat, p = stats.friedmanchisquare(*[pivot[col] for col in pivot.columns])
print(f"Friedman χ² = {stat:.3f}, p‑value = {p:.3g}")

# ---------- Pairwise Wilcoxon signed‑rank tests ----------
pairs = itertools.combinations(pivot.columns, 2)
for a, b in pairs:
    W, pval = stats.wilcoxon(pivot[a], pivot[b])
    print(f"{a} vs {b}: p = {pval:.3g}")
