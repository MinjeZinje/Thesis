import pandas as pd
from scipy.stats import shapiro

files = {
    "Static": "results_static.csv",
    "Mixed": "results_mixed.csv",
    "Breakdown": "results_breakdown.csv",
    "TimeNoise": "results_timenoise.csv",
    "NewJob": "results_newjob.csv"
}

norm_results = []

for scenario, file in files.items():
    df = pd.read_csv(file)
    for inst in df["Instance"].unique():
        inst_df = df[df["Instance"] == inst]
        for algo in inst_df["Algorithm"].unique():
            data = inst_df[inst_df["Algorithm"] == algo]["Makespan"].dropna()
            if len(data) > 3:  # Shapiro needs >3 points
                stat, p = shapiro(data)
                norm_results.append({
                    "Scenario": scenario,
                    "Instance": inst,
                    "Algorithm": algo,
                    "Shapiro-Wilk p-value": round(p, 4),
                    "Normal?": "Yes" if p > 0.05 else "No"
                })

pd.DataFrame(norm_results).to_csv("shapiro_results.csv", index=False)
print("Shapiro-Wilk normality results saved to shapiro_results.csv")
