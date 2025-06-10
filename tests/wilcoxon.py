import pandas as pd
from scipy.stats import wilcoxon, friedmanchisquare
from itertools import combinations

# Input result files
files = {
    "Static": "results_static.csv",
    "Mixed": "results_mixed.csv",
    "Breakdown": "results_breakdown.csv",
    "TimeNoise": "results_timenoise.csv",
    "NewJob": "results_newjob.csv",
}

# Store results
all_wilcoxon = []
friedman_results = []

for scenario, file_path in files.items():
    df = pd.read_csv(file_path)
    df = df.rename(columns=lambda x: x.strip())
    df["Scenario"] = scenario
    df["Run"] = df.groupby(["Instance", "Algorithm"]).cumcount()

    for instance in df["Instance"].unique():
        inst_df = df[df["Instance"] == instance]
        algos = inst_df["Algorithm"].unique()

        for a1, a2 in combinations(algos, 2):
            x = inst_df[inst_df["Algorithm"] == a1].sort_values("Run")["Makespan"]
            y = inst_df[inst_df["Algorithm"] == a2].sort_values("Run")["Makespan"]

            if len(x) == len(y) and not (x.reset_index(drop=True) == y.reset_index(drop=True)).all():
                stat, p = wilcoxon(x, y)
                sig = "Significant" if p < 0.05 else "Not significant"
                all_wilcoxon.append({
                    "Algorithm A": a1, "Algorithm B": a2, "p-value": round(p, 4),
                    "Significance": sig, "Instance": instance, "Scenario": scenario
                })

        # Friedman test
        pivot = inst_df.pivot_table(index="Run", columns="Algorithm", values="Makespan")
        if pivot.shape[1] > 2:
            stat, p = friedmanchisquare(*[pivot[col] for col in pivot.columns])
            sig = "Significant" if p < 0.05 else "Not significant"
            friedman_results.append({
                "Scenario": scenario, "Instance": instance,
                "Friedman χ²": round(stat, 4), "p-value": round(p, 4), "Significance": sig
            })

# Save results
pd.DataFrame(all_wilcoxon).to_csv("wilcoxon_all_scenarios.csv", index=False)
pd.DataFrame(friedman_results).to_csv("friedman_per_scenario.csv", index=False)
print("Wilcoxon and Friedman test results saved.")
