import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('shapiro_results.csv')

# Check the columns
print(df.columns)

# Assuming columns are ['Scenario', 'Instance', 'Algorithm', 'Shapiro p-value']
df['Rejected'] = df['Shapiro p-value'] < 0.05
grouped = df.groupby('Scenario')['Rejected'].sum()

plt.figure(figsize=(7,5))
grouped.plot(kind='bar')
plt.ylabel('Number of non-normal distributions')
plt.title('Number of makespan samples failing Shapiro–Wilk normality test')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
