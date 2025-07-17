import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../delta_vs_gamix.csv', index_col=[0, 1])
mean_deltas = df.mean().drop('GAMIX')

mean_deltas_pos = -mean_deltas.sort_values()

plt.figure(figsize=(7,4))
mean_deltas_pos.plot(kind='bar')
plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
plt.ylabel('Mean Delta to GAMIX')
plt.title('Mean Makespan Difference: Each Heuristic vs. GAMIX')

# Set y-tick labels as negative numbers
locs, labels = plt.yticks()
plt.yticks(locs, [f"{-abs(int(tick))}" for tick in locs])

plt.tight_layout()
plt.show()
