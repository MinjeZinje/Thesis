# compare_results.py
#
# Usage (from a shell / VS Code / PyCharm …):
#   python compare_results.py  old_results.csv  new_results.csv
#
# If you omit the filenames it falls back to the defaults
# you can set in DEFAULT_OLD and DEFAULT_NEW below.

import sys
import pandas as pd

# ----------------------------------------------------------------------
# 1.  Config -- change the fallback filenames if you wish
# ----------------------------------------------------------------------
DEFAULT_OLD = "results_new_job_old.csv"   # ← put the real name here
DEFAULT_NEW = "results_new_job_new.csv"   # ← put the real name here

COLUMN_NAMES = ["Instance", "Variant", "Makespan", "Scenario"]


def read_results(path: str) -> pd.DataFrame:
    """
    Read a result CSV that **may** have no header.

    We try to read the first line; if it contains the word 'Variant'
    (or any of our desired column names), we assume there *is* a header.
    Otherwise we read it again with `header=None` and set `names=COLUMN_NAMES`.
    """
    # ---- sniff the first line ----
    with open(path, "r", encoding="utf-8") as fh:
        first_line = fh.readline().strip()

    has_header = any(w.lower() in first_line.lower() for w in COLUMN_NAMES)

    if has_header:
        df = pd.read_csv(path)
    else:
        # whitespace or comma separated?  We accept either.
        df = pd.read_csv(path, sep=r"[,\s]+", header=None, names=COLUMN_NAMES,
                         engine="python")

    # Ensure correct dtypes
    df["Makespan"] = pd.to_numeric(df["Makespan"], errors="coerce")
    df["Scenario"] = pd.to_numeric(df["Scenario"], errors="coerce")
    return df


def main(old_path: str, new_path: str) -> None:
    # ------------------------------------------------------------------
    # 2.  Load both files
    # ------------------------------------------------------------------
    old_df = read_results(old_path)
    new_df = read_results(new_path)

    # ------------------------------------------------------------------
    # 3.  Aggregate - average makespan for each (instance, variant, scenario)
    # ------------------------------------------------------------------
    group_cols = ["Instance", "Variant", "Scenario"]
    old_avg = (
        old_df
        .groupby(group_cols)["Makespan"]
        .mean()
        .rename("old_avg")
    )
    new_avg = (
        new_df
        .groupby(group_cols)["Makespan"]
        .mean()
        .rename("new_avg")
    )

    # ------------------------------------------------------------------
    # 4.  Combine and compute deltas
    # ------------------------------------------------------------------
    comp = pd.concat([old_avg, new_avg], axis=1)
    comp["abs_change"] = comp["new_avg"] - comp["old_avg"]
    comp["pct_change_%"] = 100 * comp["abs_change"] / comp["old_avg"]

    # ------------------------------------------------------------------
    # 5.  Pretty print
    # ------------------------------------------------------------------
    with pd.option_context("display.max_rows", None,
                           "display.max_columns", None,
                           "display.float_format", "{:,.2f}".format):
        print("\n=== Average makespan comparison ===")
        print(comp.reset_index().to_string(index=False))

    # Optional: write to CSV
    comp.to_csv("comparison_old_vs_new.csv", index=True)
    print("\nSaved detailed table to 'comparison_old_vs_new.csv'")


if __name__ == "__main__":
    # ------------------------------------------------------------------
    # 6.  Parse arguments
    # ------------------------------------------------------------------
    if len(sys.argv) == 3:
        old_file, new_file = sys.argv[1], sys.argv[2]
    else:
        old_file, new_file = DEFAULT_OLD, DEFAULT_NEW
        print(f"(No filenames given – using defaults: {old_file!r}, {new_file!r})")

    main(old_file, new_file)
