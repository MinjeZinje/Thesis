import pandas as pd, numpy as np
from itertools import combinations
from scipy import stats

def norm(s): return s.lower().strip().replace(" ", "").replace("_", "")
def find_col(cols, *cands):
    nmap = {norm(c): c for c in cols}
    for c in cands:
        if norm(c) in nmap: return nmap[norm(c)]
    return None

df = pd.read_csv("summary.csv")

inst = find_col(df.columns, "instance")
scen = find_col(df.columns, "scenario")
algo = find_col(df.columns, "algorithm")
mk   = find_col(df.columns, "makespan", "avg_makespan", "average makespan",
                "mean", "mean_makespan", "final makespan", "MeanMakespan", "meanmakespan")

# fallback: pick the first numeric column that isn’t one of the keys
if not mk:
    keyset = {inst, scen, algo}
    numcands = [c for c in df.columns if c not in keyset and pd.to_numeric(df[c], errors="coerce").notna().any()]
    if not numcands:
        raise KeyError(f"Missing makespan-like column. Found: {list(df.columns)}")
    mk = numcands[0]

# ensure numeric makespan
df[mk] = pd.to_numeric(df[mk], errors="coerce")

pivot = df.pivot_table(values=mk, index=[inst, scen], columns=algo, aggfunc="mean").dropna()
algs = list(pivot.columns)
X = pivot.values
N, k = X.shape

fried_stat, fried_p = stats.friedmanchisquare(*[pivot[c] for c in algs])
print(f"Friedman χ²({k-1}) = {fried_stat:.3f}, p = {fried_p:.3g}")

row_ranks = np.apply_along_axis(lambda r: stats.rankdata(r, method="average"), 1, X)
row_ranks = k + 1 - row_ranks
avg_ranks = row_ranks.mean(axis=0)
print("\nAverage ranks (higher = better):")
print(pd.DataFrame({"Algorithm": algs, "AvgRank": avg_ranks}).sort_values("AvgRank", ascending=False).to_string(index=False))

q_alpha = 2.728
CD = q_alpha * np.sqrt(k*(k+1)/(6*N))
print(f"\nNemenyi CD (α=0.05): {CD:.3f}")

def wilcoxon_r_rank_biserial(a, b):
    diff = a - b
    mask = diff != 0
    diffs = diff[mask]
    if diffs.size == 0: return np.nan, np.nan, np.nan
    ranks = stats.rankdata(np.abs(diffs))
    Wp = ranks[diffs > 0].sum(); Wm = ranks[diffs < 0].sum()
    r_rb = (Wp - Wm) / (Wp + Wm)
    W, p = stats.wilcoxon(a, b, zero_method="pratt", alternative="two-sided", correction=False)
    return W, p, r_rb

pairs, rows = list(combinations(algs, 2)), []
for a, b in pairs:
    W, p, rrb = wilcoxon_r_rank_biserial(pivot[a].values, pivot[b].values)
    rows.append({"A": a, "B": b, "W": W, "p_raw": p, "r_rank_biserial": rrb})
res = pd.DataFrame(rows)

# Holm–Bonferroni (step-down)
m, order = len(res), np.argsort(res["p_raw"].values)
adj = np.empty(m); max_adj = 0.0
for i, idx in enumerate(order):
    adj_i = min((m - i) * res.loc[idx, "p_raw"], 1.0)
    max_adj = max(max_adj, adj_i)
    adj[idx] = max_adj
res["p_holm"] = adj
res["sig_0.05"] = res["p_holm"] < 0.05
print("\nPairwise Wilcoxon (Holm) + rank-biserial:")
print(res.sort_values("p_holm")[["A","B","W","p_raw","p_holm","sig_0.05","r_rank_biserial"]].to_string(index=False))
