import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

nemenyi = pd.read_csv('nemenyi_posthoc_results.csv')
print(nemenyi['Scenario'].unique())
print(nemenyi['Instance'].unique())

scenario = 'Breakdown '   # Use exactly as printed
instance = ('la30')     # Use exactly as printed

subset = nemenyi[(nemenyi['Scenario'] == scenario) & (nemenyi['Instance'] == instance)]
print(subset)

algorithms = sorted(list(set(subset['Alg1']).union(set(subset['Alg2']))))
if not algorithms:
    print("No matching rows found. Check your scenario and instance spelling.")
else:
    heat = pd.DataFrame(0, index=algorithms, columns=algorithms)
    for _, row in subset.iterrows():
        # Use the correct column name for the p-value
        if row['Nemenyi p-value'] < 0.05:
            heat.loc[row['Alg1'], row['Alg2']] = 1
            heat.loc[row['Alg2'], row['Alg1']] = 1

    plt.figure(figsize=(8,6))
    sns.heatmap(heat, annot=True, cmap='Reds', cbar=False)
    plt.title(f'Significant Pairwise Differences (Nemenyi, {scenario}, {instance})')
    plt.xlabel('Algorithm')
    plt.ylabel('Algorithm')
    plt.show()
