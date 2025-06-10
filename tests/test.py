import pandas as pd
from pathlib import Path

# --------------------------------------------------------------------------- #
#  Benchmark best-known makespans                                             #
# --------------------------------------------------------------------------- #
BEST_KNOWN = {
    "ft06": 55, "ft10": 930, "ft20": 1165,
    "la01": 666, "la10": 958, "la20": 902, "la30": 1355,
}

# CSVs produced by main.py
FILES = {
    "Static":    "results/results_static.csv",
    "Mixed":     "results/results_mixed.csv",
    "Breakdown": "results/results_breakdown.csv",
    "TimeNoise": "results/results_timenoise.csv",
    "NewJob":    "results/results_newjob.csv",
}

# --------------------------------------------------------------------------- #
def load(path: str) -> pd.DataFrame:
    """Load a results CSV and keep only the seven benchmark instances."""
    df = pd.read_csv(path)
    return df[df["Instance"].isin(BEST_KNOWN)]

# --------------------------------------------------------------------------- #
# 1) STATIC SUMMARY (mean + SD %)                                             #
# --------------------------------------------------------------------------- #
static_df = load(FILES["Static"])
stat_agg = (static_df.groupby(["Instance", "Algorithm"])["Makespan"]
                      .agg(["mean", "std"]).round(2))
stat_agg["SD%"] = (stat_agg["std"] / stat_agg["mean"] * 100).round(2)
stat_agg = stat_agg.drop(columns="std").reset_index()

wide = stat_agg.pivot(index="Instance", columns="Algorithm")
static_tbl = pd.DataFrame(index=wide.index)
for alg in wide.columns.levels[1]:
    static_tbl[f"{alg} Mean"] = wide[("mean", alg)]
    static_tbl[f"{alg} SD%"]  = wide[("SD%",  alg)]
static_tbl.insert(0, "Best Known", [BEST_KNOWN[i] for i in static_tbl.index])
static_tbl.reset_index(inplace=True)
static_tbl.insert(0, "Scenario", "Static")

# Keep baseline means for dynamic gap calculations
baseline_mean = stat_agg.set_index(["Instance", "Algorithm"])["mean"]

# --------------------------------------------------------------------------- #
# 2) DYNAMIC SCENARIOS (Mean % gain + SD)                                     #
# --------------------------------------------------------------------------- #
dyn_tables = []
for scen, path in FILES.items():
    if scen == "Static":
        continue
    df = load(path)
    # compute percentage gain over static GA baseline
    df["Base"] = [baseline_mean.get((i, a)) for i, a in zip(df["Instance"], df["Algorithm"])]
    df["Gain%"] = (df["Makespan"] - df["Base"]) / df["Base"] * 100
    agg = (df.groupby(["Instance", "Algorithm"])["Gain%"]
             .agg(["mean", "std"]).round(2).reset_index())
    wide = agg.pivot(index="Instance", columns="Algorithm")
    tbl = pd.DataFrame(index=wide.index)
    for alg in wide.columns.levels[1]:
        tbl[f"{alg} Mean%"] = wide[("mean", alg)]
        tbl[f"{alg} SD"]    = wide[("std",  alg)]
    tbl.reset_index(inplace=True)
    tbl.insert(0, "Scenario", scen)
    dyn_tables.append(tbl)

# --------------------------------------------------------------------------- #
# 3) WRITE results_summary.xlsx                                               #
# --------------------------------------------------------------------------- #
summary_path = Path("results_summary.xlsx")
with pd.ExcelWriter(summary_path) as xl:
    static_tbl.to_excel(xl, sheet_name="Static", index=False)
    for tbl in dyn_tables:
        scen = tbl.iloc[0, 0]          # Scenario name in first column
        tbl.to_excel(xl, sheet_name=scen, index=False)
print(f"✓ wrote {summary_path}")

# --------------------------------------------------------------------------- #
# 4) AVERAGES-ONLY TABLE (no SD)                                              #
# --------------------------------------------------------------------------- #
avg_rows = []
for scen, path in FILES.items():
    df = load(path)
    avg = (df.groupby(["Instance", "Algorithm"])["Makespan"]
             .mean().unstack().round(2).reset_index())
    avg.insert(0, "Scenario", scen)
    avg.insert(2, "Best Known", [BEST_KNOWN[i] for i in avg["Instance"]])
    avg_rows.append(avg)

avg_only = pd.concat(avg_rows, ignore_index=True)
avg_path = Path("results_summary_avg_only.xlsx")
avg_only.to_excel(avg_path, index=False)
print(f"✓ wrote {avg_path}")
