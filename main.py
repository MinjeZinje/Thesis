# main.py  – clean v3  (2025-06-06)
from __future__ import annotations
import os, csv, copy, random, statistics, tempfile
from typing import Dict, Tuple
from multiprocessing import Pool

from loader      import load_instances
from heuristics  import HEURISTICS
from ga          import GeneticAlgorithm
from scheduler   import Scheduler
from rescheduler import simulate_with_rescheduling, simulate_ts_with_rescheduling
from tabu        import run_tabu_search

random.seed(42)
REPS = 20

SCENARIOS: Dict[str, int] = {
    "Static":     0,
    "NewJob":     1,
    "Breakdown":  2,
    "TimeNoise":  3,
    "Mixed":      4,        # all events together
}

# ------------------------------------------------------------------  GA helper
def _ga_static_once(data: dict, heuristic) -> int:
    ga = GeneticAlgorithm(
        data,
        pop_size=200, num_generations=1_000,
        crossover_rate=0.95, mutation_rate=0.05,
        elitism_rate=0.10,   local_search_swaps=30,
        seed_ratio=0.25,
    )
    sched = Scheduler(num_machines=data["num_machines"])
    _, mk = ga.run(data, sched, heuristic)
    return mk


def _one_ga_run(args: Tuple[dict, int, str, callable]) -> int:
    instance, scen_id, vname, hfun = args
    inst = copy.deepcopy(instance)
    if scen_id == 0:                       # static
        return _ga_static_once(inst, hfun)
    # dynamic
    hist = simulate_with_rescheduling(
        inst, scenario_id=scen_id,
        variant_name=vname,
        heuristic_func=hfun,
        max_time=100,
    )
    return hist[-1][1]                    # makespan after final event

# ------------------------------------------------------------------  TS helper
def _ts_static_once(data: dict) -> int:
    tmp = tempfile.NamedTemporaryFile(delete=False).name   # dummy csv path
    return run_tabu_search(data, data["name"], tmp, 0)[0][2]


def _ts_dynamic_once(data: dict, scen_id: int) -> int:
    hist = simulate_ts_with_rescheduling(data, scenario_id=scen_id, max_time=100)
    return hist[-1][1]


def _one_ts_run(args: Tuple[dict, int]) -> int:
    inst, sid = args
    dat = copy.deepcopy(inst)
    return _ts_static_once(dat) if sid == 0 else _ts_dynamic_once(dat, sid)

# --------------------------------------------------------------------------- #
def main() -> None:
    instances = load_instances("data.txt")
    os.makedirs("results", exist_ok=True)

    writers, files = {}, {}
    for scen, sid in SCENARIOS.items():
        f = open(f"results/results_{scen.lower()}.csv", "w", newline="")
        w = csv.writer(f)
        w.writerow(["Instance", "Algorithm", "Makespan", "ScenarioID"])
        writers[sid], files[sid] = w, f

    for inst in instances:
        print(f"\n▶ Instance {inst['name']} — {inst['num_jobs']}×{inst['num_machines']}")
        for scen_name, sid in SCENARIOS.items():
            print(f"  Scenario: {scen_name}")
            out_csv = writers[sid]

            # ---------- GA variants
            for vname, hfun in HEURISTICS.items():
                args = [(inst, sid, vname, hfun)] * REPS
                with Pool() as pool:
                    scores = pool.map(_one_ga_run, args)
                for mk in scores:
                    out_csv.writerow([inst["name"], vname, mk, sid])
                print(f"    {vname:<7} avg={statistics.mean(scores):.2f} "
                      f"sd={statistics.pstdev(scores):.2f}")

            # ---------- TS baseline
            ts_args = [(inst, sid)] * REPS
            with Pool() as pool:
                ts_scores = pool.map(_one_ts_run, ts_args)
            for mk in ts_scores:
                out_csv.writerow([inst["name"], "TS", mk, sid])
            print(f"    TS      avg={statistics.mean(ts_scores):.2f} "
                  f"sd={statistics.pstdev(ts_scores):.2f}")

    for f in files.values():
        f.close()


if __name__ == "__main__":
    main()
