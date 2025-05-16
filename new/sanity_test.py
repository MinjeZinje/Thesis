# sanity_check.py  – quick 1-minute run
import copy, statistics
from loader import load_instances
from rescheduler import simulate_with_rescheduling
from heuristics import HEURISTICS               # GA variants
from ga import GeneticAlgorithm, run_tabu_search

REPS = 3
INST = "ft06"
SCENARIO = 4          # mixed: arrivals+breakdowns+noise

data = load_instances("data.txt")[INST]
data["name"] = INST

print(f"\n=== Sanity test on {INST} / scenario {SCENARIO} ===")
for vname, hfunc in HEURISTICS.items():
    scores = []
    for _ in range(REPS):
        d = copy.deepcopy(data)
        ga = GeneticAlgorithm(d, num_generations=10)    # 10 gens
        hist = simulate_with_rescheduling(d, SCENARIO, vname, hfunc, max_time=50)
        scores.append(hist[-1][1])
    print(f"{vname}: avg {statistics.mean(scores):.2f}, std {statistics.pstdev(scores):.2f}")

# quick TS
ts_scores = []
for _ in range(REPS):
    d = copy.deepcopy(data)
    row = run_tabu_search(d, INST, "_dummy.csv", SCENARIO)
    ts_scores.append(row[0][2])
print(f"TS : avg {statistics.mean(ts_scores):.2f}, std {statistics.pstdev(ts_scores):.2f}")
