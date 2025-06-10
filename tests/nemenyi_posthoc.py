import pandas as pd
import scikit_posthocs as sp
from scipy.stats import friedmanchisquare

files = {
    "Static": "results_static.csv",
    "Mixed": "results_mixed.csv",
    "Breakdown": "results_breakdown.csv",
    "TimeNoise": "results_timenoise.csv",
    "NewJob": "results_newjob.csv"
}

nemenyi_results = []

for scenario, file in files.items():
    df = pd.read_csv(file)
    for inst in df["Instance"].unique():
        inst_df = df[df["Instance"] == inst]
        # If "Run" is missing, create it
        if "Run" not in inst_df.columns:
            inst_df = inst_df.copy()
            inst_df["Run"] = inst_df.groupby(["Instance", "Algorithm"]).cumcount()
        pivot = inst_df.pivot_table(index="Run", columns="Algorithm", values="Makespan")
        if pivot.shape[1] > 2:
            data = [pivot[alg].dropna() for alg in pivot.columns]
            min_len = min(len(d) for d in data)
            if min_len > 3:
                trimmed = [d.iloc[:min_len] for d in data]
                stat, p = friedmanchisquare(*trimmed)
                if p < 0.05:
                    nemenyi = sp.posthoc_nemenyi_friedman(pivot.values)
                    nemenyi.index = nemenyi.columns = pivot.columns
                    for a1 in nemenyi.index:
                        for a2 in nemenyi.columns:
                            if a1 != a2 and a1 < a2:  # Avoid duplicates
                                pval = nemenyi.loc[a1, a2]
                                result = "Significant" if pval < 0.05 else "Not significant"
                                nemenyi_results.append({
                                    "Scenario": scenario,
                                    "Instance": inst,
                                    "Algorithm A": a1,
                                    "Algorithm B": a2,
                                    "Nemenyi p-value": round(pval, 4),
                                    "Significance": result
                                })

pd.DataFrame(nemenyi_results).to_csv("nemenyi_posthoc_results.csv", index=False)
print("Nemenyi post-hoc results saved to nemenyi_posthoc_results.csv")
