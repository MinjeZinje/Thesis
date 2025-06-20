import pandas as pd
import matplotlib.pyplot as plt

# Load Friedman results
df_friedman = pd.read_csv('friedman_per_scenario.csv')

# For each scenario, count where p-value < 0.05
sig_counts = df_friedman.groupby('Scenario').apply(lambda g: (g['p-value'] < 0.05).sum())
total_counts = df_friedman.groupby('Scenario')['Instance'].count()
proportions = sig_counts / total_counts

plt.figure(figsize=(8,5))
sig_counts.plot(kind='bar')
plt.ylabel('Number of significant instances')
plt.title('Number of instances with significant algorithmic differences (Friedman test)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
