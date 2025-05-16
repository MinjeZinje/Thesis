import pandas as pd
import scipy.stats as stats
import glob
import os
from itertools import combinations

REPS = 20  # Number of repetitions per variant

def run_paired_t_tests(input_path):
    # Extract scenario name from file name
    scenario = os.path.splitext(os.path.basename(input_path))[0].replace("results_", "")
    df = pd.read_csv(input_path, header=None, names=["Instance", "Variant", "Makespan", "Scenario_ID"])

    results = {}

    for instance in df["Instance"].unique():
        df_inst = df[df["Instance"] == instance]
        grouped = df_inst.groupby("Variant")["Makespan"]

        # Keep only complete variant groups
        variant_data = {v: g.values for v, g in grouped if len(g) == REPS}

        for var1, var2 in combinations(variant_data.keys(), 2):
            try:
                t_stat, p_val = stats.ttest_rel(variant_data[var1], variant_data[var2])
                key = f"{var1} vs {var2}"
                if key not in results:
                    results[key] = []
                results[key].append((t_stat, p_val))
            except ValueError:
                continue

    # Average results across instances
    final = {
        k: (sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v))
        for k, v in results.items() if len(v) > 0
    }

    result_df = pd.DataFrame.from_dict(final, orient='index', columns=['avg_t_stat', 'avg_p_value'])
    result_df = result_df.sort_values(by='avg_p_value')
    result_df.to_csv(f"ttest_{scenario}.csv")
    print(f"Saved: ttest_{scenario}.csv")


if __name__ == "__main__":
    for file in glob.glob("results_*.csv"):
        run_paired_t_tests(file)
