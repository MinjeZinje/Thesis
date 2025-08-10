from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE          = Path(__file__).resolve().parent
SUMMARY_FILE  = HERE / "results_summary_avg_only.xlsx"   # <— new workbook
DELTA_FILE    = HERE / "delta_vs_gamix.csv"              # diagnostic ablation
OUTDIR        = HERE / "figures"
OUTDIR.mkdir(exist_ok=True)

# Order shown on x-axis (single-heuristic figure)
ALG_ORDER = ["GA", "GAKK", "GASPT", "GASRPT", "GALRPT", "GALPT"]

# ----------------------------------------------------------------------
def ci95(series: pd.Series) -> float:
    if len(series) <= 1:
        return 0.0
    se = series.std(ddof=1) / np.sqrt(series.count())
    return 1.96 * se

#  FIGURE A – Single-heuristic Δ (variant – GAMIX)

def single_plot():
    if not SUMMARY_FILE.exists():
        print(f"[WARN] {SUMMARY_FILE} not found – skipping Figure A")
        return

    # -------- load workbook (any sheet) --------
    df = pd.read_excel(SUMMARY_FILE, sheet_name=0)
    df.columns = [c.strip() for c in df.columns]   # trim spaces

    # -------- identify algorithm columns --------
    alg_cols = [c for c in df.columns
                if c.strip().upper() in [a.upper() for a in ALG_ORDER + ["GAMIX"]]]
    if not alg_cols:
        raise ValueError("No algorithm columns found in the summary workbook.")
    id_cols = [c for c in df.columns if c not in alg_cols]

    # supply missing columns if summary already averaged (e.g. Scenario missing)
    if "Instance" not in id_cols:
        df.insert(0, "Instance", "AVG")
        id_cols.insert(0, "Instance")
    if "Scenario" not in id_cols:
        df.insert(1, "Scenario", "ALL")
        id_cols.insert(1, "Scenario")

    # -------- long → compute Δ --------
    long = df.melt(id_vars=id_cols, value_vars=alg_cols,
                   var_name="Algorithm", value_name="Makespan")

    piv = long.pivot_table(index=id_cols, columns="Algorithm", values="Makespan")

    gamix_col = next((c for c in piv.columns if c.strip().lower() == "gamix"), None)
    if gamix_col is None:
        raise KeyError("No GAMIX column found in the summary workbook.")

    piv = piv.dropna(subset=[gamix_col])
    delta = piv[[c for c in ALG_ORDER if c in piv.columns]].subtract(
                piv[gamix_col], axis=0)

    stats = (delta.melt(value_name="Delta")
                   .groupby("Algorithm")["Delta"]
                   .agg(MeanDelta="mean", CI95=ci95, N="count")
                   .reindex([a for a in ALG_ORDER if a in delta.columns])
                   .reset_index())

    stats.to_csv(OUTDIR / "single_vs_gamix_stats.csv", index=False)

    # -------- plot --------
    plt.figure(figsize=(9, 4.6))
    plt.bar(stats["Algorithm"], stats["MeanDelta"],
            yerr=stats["CI95"], capsize=3, color="#4682B4")
    plt.axhline(0, color="k", lw=1, ls="--")
    plt.ylabel("Mean Δ vs GAMIX (time units)")
    plt.title("Single-heuristic GA variants – Δ = variant − GAMIX\n(negative = better)")
    plt.xticks(rotation=40, ha="right")
    plt.tight_layout()
    out_png = OUTDIR / "single_vs_gamix.png"
    plt.savefig(out_png, dpi=220)
    plt.close()
    print("[saved]", out_png)

#  FIGURE B – Leave-one-out ablation (delta_vs_gamix.csv)

def ablation_plot():
    if not DELTA_FILE.exists():
        print(f"[WARN] {DELTA_FILE} not found – skipping Figure B")
        return

    df = pd.read_csv(DELTA_FILE)
    abl_cols = [c for c in df.columns if c.startswith("GAMIX_no_")]
    id_cols  = [c for c in ["Scenario", "Instance"] if c in df.columns]

    long = df.melt(id_vars=id_cols, value_vars=abl_cols,
                   var_name="Algorithm", value_name="Delta")

    stats = (long.groupby("Algorithm")["Delta"]
                  .agg(MeanDelta="mean", CI95=ci95, N="count")
                  .sort_values("MeanDelta")
                  .reset_index())

    stats.to_csv(OUTDIR / "ablation_delta_vs_gamix_stats.csv", index=False)

    plt.figure(figsize=(10, 4.6))
    plt.bar(stats["Algorithm"], stats["MeanDelta"],
            yerr=stats["CI95"], capsize=3, color="#009E73")
    plt.axhline(0, color="k", lw=1, ls="--")
    plt.ylabel("Mean Δ vs GAMIX (time units)")
    plt.title("Leave-one-out ablation – Δ = variant − GAMIX")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    out_png = OUTDIR / "ablation_delta_vs_gamix.png"
    plt.savefig(out_png, dpi=220)
    plt.close()
    print("[saved]", out_png)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    single_plot()   # Figure A
    ablation_plot() # Figure B
