import pandas as pd
from scipy.stats import wilcoxon
from itertools import combinations
import glob
import os

REPS = 20  # Expected repetitions per variant

def run_wilcoxon_tests(input_path):
    scenario = os.path.splitext(os.path.basename(input_path))[0].replace("results_", "")
    df = pd.read_csv(input_path, header=None, names=["Instance", "Variant", "Makespan", "Scenario_ID"])

    results = {}

    for instance in df["Instance"].unique():
        df_inst = df[df["Instance"] == instance]
        grouped = df_inst.groupby("Variant")["Makespan"]
        variant_data = {v: g.values for v, g in grouped if len(g) == REPS}

        for var1, var2 in combinations(variant_data.keys(), 2):
            try:
                stat, p_val = wilcoxon(variant_data[var1], variant_data[var2])
                key = f"{var1} vs {var2}"
                if key not in results:
                    results[key] = []
                results[key].append((stat, p_val))
            except ValueError:
                continue  # e.g., identical samples

    # Average across instances
    final = {
        k: (sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v))
        for k, v in results.items() if len(v) > 0
    }

    result_df = pd.DataFrame.from_dict(final, orient='index', columns=['avg_stat', 'avg_p_value'])
    result_df = result_df.sort_values(by='avg_p_value')
    result_df.to_csv(f"wilcoxon_{scenario}.csv")
    print(f"Saved: wilcoxon_{scenario}.csv")


if __name__ == "__main__":
    for file in glob.glob("results_*.csv"):
        run_wilcoxon_tests(file)
