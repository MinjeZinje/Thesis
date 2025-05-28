"""
stat_analysis.py
Compares algorithm variants in each results_*.csv file using
paired t-tests and Wilcoxon signed-rank tests.

Expected CSV columns   (order doesn’t matter):
    Instance, Variant, Best_makespan, Scenario
If the file has no header row, the script adds it automatically.
"""

from pathlib import Path
from itertools import combinations
import pandas as pd
from scipy import stats

# ----------- helper ----------------------------------------------------------

def load_results(csv_path: Path) -> pd.DataFrame:
    """
    Read a result file, adding a header if one is missing.
    """
    cols = ["Instance", "Variant", "Best_makespan", "Scenario"]

    # Try with header.  If “Instance” not in columns → reload w/ header=None.
    df = pd.read_csv(csv_path)
    if "Instance" not in df.columns:
        df = pd.read_csv(csv_path, header=None, names=cols)

    # Ensure correct dtypes
    df["Best_makespan"] = pd.to_numeric(df["Best_makespan"], errors="coerce")
    df["Scenario"]      = pd.to_numeric(df["Scenario"],      errors="coerce")
    return df[cols]


def pairwise_tests(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    For each instance & scenario, perform:
      • paired t-test
      • Wilcoxon signed-rank test
    between every pair of variants.

    Returns two long-format DataFrames (t-test, wilcoxon).
    """
    t_rows, w_rows = [], []

    for (inst, scen), sub in df.groupby(["Instance", "Scenario"]):
        pivot = sub.pivot_table(index="rep",  # rep column added below
                                columns="Variant",
                                values="Best_makespan")
        variants = pivot.columns

        for v1, v2 in combinations(variants, 2):
            # Drop rows with any NaN for the pair
            paired = pivot[[v1, v2]].dropna()

            if len(paired) < 2:
                continue  # not enough data

            # Paired t-test
            t_stat, t_p = stats.ttest_rel(paired[v1], paired[v2])
            # Wilcoxon
            try:
                w_stat, w_p = stats.wilcoxon(paired[v1], paired[v2])
            except ValueError:  # all zeros, etc.
                w_stat, w_p = float("nan"), float("nan")

            t_rows.append(
                dict(Instance=inst, Scenario=scen,
                     Pair=f"{v1} vs {v2}", t_stat=t_stat, p_value=t_p,
                     n=len(paired))
            )
            w_rows.append(
                dict(Instance=inst, Scenario=scen,
                     Pair=f"{v1} vs {v2}", W=w_stat, p_value=w_p,
                     n=len(paired))
            )

    t_df = pd.DataFrame(t_rows)
    w_df = pd.DataFrame(w_rows)
    return t_df, w_df


def add_rep_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a 'rep' column (0 … r-1) so that pivot_table can align
    paired runs from the same replication number.
    """
    df = df.copy()
    df["rep"] = df.groupby(["Instance", "Scenario", "Variant"]).cumcount()
    return df


# ----------- main -----------------------------------------------------------

def main():
    # Any CSV whose name starts with “results_” is analysed
    for csv_path in Path(".").glob("results_*.csv"):
        print(f"\n=== {csv_path.name} ===")

        df = load_results(csv_path)
        df = add_rep_column(df)

        t_df, w_df = pairwise_tests(df)

        # Save
        t_out = csv_path.with_name(f"ttest_{csv_path.stem}.csv")
        w_out = csv_path.with_name(f"wilcoxon_{csv_path.stem}.csv")
        t_df.to_csv(t_out, index=False)
        w_df.to_csv(w_out, index=False)

        # Pretty print a short summary
        print(f"Saved t-tests   → {t_out}")
        print(f"Saved Wilcoxon → {w_out}")

        # Show top 5 most significant pairs (lowest p)
        if not t_df.empty:
            print("\nTop 5 (paired t-test, by p-value):")
            print(t_df.sort_values("p_value").head(5).to_string(index=False))


if __name__ == "__main__":
    main()
