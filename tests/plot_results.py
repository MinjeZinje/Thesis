import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 1. load raw rows
df = pd.read_csv(
    "results_static.csv",
    names=["Instance", "Variant", "BestMakespan", "Scenario"],
    header=None
)
best_per_inst = df.groupby("Instance")["BestMakespan"].transform("min")
df["GapPercent"] = (df["BestMakespan"] - best_per_inst) / best_per_inst * 100

# --- NEW: aggregate so every Instance–Variant is unique
agg = (
    df.groupby(["Instance", "Variant"], as_index=False)["GapPercent"]
      .mean()          # mean across the 20 replications
)

out = Path("plots"); out.mkdir(exist_ok=True)

# 2a heat-map (no duplicates now)
pivot = agg.pivot(index="Instance", columns="Variant", values="GapPercent")
plt.figure(figsize=(8, 5))
plt.imshow(pivot.values, cmap="viridis_r", aspect="auto")
plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
plt.yticks(range(len(pivot.index)), pivot.index)
plt.colorbar(label="% gap to best")
plt.title("Static scenario – gap heat-map")
plt.tight_layout()
plt.savefig(out / "static_gap_heatmap.png", dpi=300)
plt.close()

# 2b mean ± SD bar chart (use raw df ⇒ proper SD across reps)
means = df.groupby("Variant")["GapPercent"].mean()
stds  = df.groupby("Variant")["GapPercent"].std()
plt.figure(figsize=(8, 4))
plt.bar(means.index, means, yerr=stds, capsize=3)
plt.ylabel("Average % gap to best")
plt.title("Static scenario – mean ± 1 SD")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(out / "static_gap_bar.png", dpi=300)
plt.close()

# 2c per-instance line plot (use agg so one point per inst)
plt.figure(figsize=(9, 5))
for v, sub in agg.groupby("Variant"):
    sub = sub.sort_values("Instance")
    plt.plot(sub["Instance"], sub["GapPercent"], marker="o", label=v)
plt.ylabel("% gap to best")
plt.xlabel("Instance")
plt.title("Static scenario – per-instance profile")
plt.legend(ncol=4, fontsize="small")
plt.tight_layout()
plt.savefig(out / "static_gap_lines.png", dpi=300)
plt.close()

print("All three plots saved to", out.resolve())
