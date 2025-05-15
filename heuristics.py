import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import glob

sns.set(style="whitegrid")

def plot_boxplots():
    for filepath in glob.glob("results_*.csv"):
        scenario = os.path.splitext(os.path.basename(filepath))[0].replace("results_", "")
        df = pd.read_csv(filepath, header=None, names=["Instance", "Variant", "Makespan", "Scenario_ID"])

        plt.figure(figsize=(10, 6))
        sns.boxplot(data=df, x="Variant", y="Makespan", palette="pastel")
        plt.title(f"Makespan Distribution per Variant - {scenario.capitalize()} Scenario")
        plt.ylabel("Makespan")
        plt.xlabel("Variant")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f"boxplot_{scenario}.png")
        plt.close()
        print(f"Saved: boxplot_{scenario}.png")

if __name__ == "__main__":
    plot_boxplots()
