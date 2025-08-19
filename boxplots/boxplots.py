# boxplots_all.py
import os
import pandas as pd
import matplotlib.pyplot as plt

# ---- config ----
INPUTS = {
    "Static": "results_static.csv",
    "NewJob": "results_newjob.csv",
    "Breakdown": "results_breakdown.csv",
    "TimeNoise": "results_timenoise.csv",
    "Mixed": "results_mixed.csv",
}
OUTDIR = "figures/boxplots"
ALGO_ORDER = ["GA","GAKK","GALPT","GALRPT","GAMIX","GASPT","GASRPT","TS"]  # edit if needed

os.makedirs(OUTDIR, exist_ok=True)

def clean_cols(df):
    # tolerate various column namings
    cols = {c.lower(): c for c in df.columns}
    def pick(*names):
        for n in names:
            if n.lower() in cols: return cols[n.lower()]
        raise KeyError(f"Missing column among {names}; found: {list(df.columns)}")

    inst = pick("Instance")
    algo = pick("Algorithm","Alg")
    mksp = pick("Makespan","Cmax","Final Makespan","makespan_final")

    df = df.rename(columns={inst:"Instance", algo:"Algorithm", mksp:"Makespan"})
    # coerce types
    df["Instance"] = df["Instance"].astype(str)
    df["Algorithm"] = df["Algorithm"].astype(str)
    df["Makespan"] = pd.to_numeric(df["Makespan"], errors="coerce")
    df = df.dropna(subset=["Makespan"])
    return df

def order_algos(df):
    seen = [a for a in ALGO_ORDER if a in df["Algorithm"].unique().tolist()]
    # append any extras at the end
    extras = [a for a in df["Algorithm"].unique().tolist() if a not in seen]
    return seen + sorted(extras)

def plot_one(df_inst, scenario, instance, algo_order):
    data = [df_inst.loc[df_inst["Algorithm"]==a, "Makespan"].values for a in algo_order]
    labels = algo_order
    plt.figure(figsize=(6.4,4.8))
    bp = plt.boxplot(data, labels=labels, patch_artist=False, showfliers=True)
    plt.title(f"{scenario} Scenario - Makespan Distribution for {instance}")
    plt.xlabel("Algorithm")
    plt.ylabel("Makespan")
    plt.tight_layout()
    fname = os.path.join(OUTDIR, f"boxplot_{scenario.lower()}_{instance.lower().replace(' ','')}.png")
    plt.savefig(fname, dpi=200)
    plt.close()
    print("Saved:", fname)

for scenario, path in INPUTS.items():
    if not os.path.exists(path):
        print(f"WARNING: {path} not found; skipping {scenario}.")
        continue
    df = pd.read_csv(path)
    df = clean_cols(df)

    # force instance names uppercase (e.g. ft06 → FT06, la10 → LA10)
    df["Instance"] = df["Instance"].str.upper()

    for inst, df_inst in df.groupby("Instance", sort=False):
        algo_order = order_algos(df_inst)
        plot_one(df_inst, scenario, inst, algo_order)

