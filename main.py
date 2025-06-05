# main.py
from __future__ import annotations
import os, csv, copy, random, statistics
from typing import Dict
from multiprocessing import Pool
from tqdm import trange

from loader import load_instances
from heuristics import HEURISTICS, kk_heuristic
from ga import GeneticAlgorithm
from rescheduler import simulate_with_rescheduling
from scheduler import Scheduler
from tabu import run_tabu_search


random.seed(42)
REPS = 20

SCENARIOS: Dict[str, int] = {
    "Static": 0,
    "Mixed": 4,
    "Breakdown": 2,
    "TimeNoise": 3,
    "NewJob": 1,
}


def ga_static_once(data: dict, heuristic) -> int:
    ga = GeneticAlgorithm(
        data,
        pop_size=200,
        num_generations=1000,
        crossover_rate=0.95,
        mutation_rate=0.05,
        elitism_rate=0.10,
        local_search_swaps=30,
        seed_ratio=0.25,
    )
    sched = Scheduler(num_machines=data["num_machines"])
    _, mk = ga.run(data, sched, heuristic)   # ➋ keep this order
    return mk


def one_ga_run(args):
    instance, scen_id, vname, hfun = args
    inst_cp = copy.deepcopy(instance)
    if scen_id == 0:
        return ga_static_once(inst_cp, hfun)
    return simulate_with_rescheduling(inst_cp, scen_id, vname, hfun, max_time=100)[-1][1]


def one_tabu_run(args):
    instance, name, path, scen_id = args
    inst_cp = copy.deepcopy(instance)
    return run_tabu_search(inst_cp, name, path, scen_id)[0][2]


def main():
    instances = load_instances("data.txt")
    os.makedirs("results", exist_ok=True)

    writers, files = {}, {}
    for scen, sid in SCENARIOS.items():
        f = open(f"results/results_{scen.lower()}.csv", "w", newline="")
        w = csv.writer(f)
        w.writerow(["Instance", "Algorithm", "Makespan", "ScenarioID"])
        writers[sid], files[sid] = w, f

    for instance in instances:
        print(f"\n▶ Instance {instance['name']} — {instance['num_jobs']}×{instance['num_machines']}")

        for scen_name, sid in SCENARIOS.items():
            print(f"  Scenario: {scen_name}")
            out_csv = writers[sid]

            # --- GA variants in parallel
            for vname, hfun in HEURISTICS.items():
                print(f"    {vname:<7}", end=" ", flush=True)
                args = [(instance, sid, vname, hfun)] * REPS
                with Pool(processes=6) as pool:
                    scores = list(pool.map(one_ga_run, args))

                for mk in scores:
                    out_csv.writerow([instance["name"], vname, mk, sid])

                print(f"avg={statistics.mean(scores):.2f} "
                      f"sd={statistics.pstdev(scores):.2f}")

            # --- Tabu baseline in parallel
            print(f"    TS     ", end=" ", flush=True)
            ts_args = [(instance, instance["name"], f"results/results_{scen_name.lower()}.csv", sid)] * REPS
            with Pool(processes=6) as pool:
                ts_scores = list(pool.map(one_tabu_run, ts_args))

            for mk in ts_scores:
                out_csv.writerow([instance["name"], "TS", mk, sid])

            print(f"avg={statistics.mean(ts_scores):.2f} "
                  f"sd={statistics.pstdev(ts_scores):.2f}")

    for f in files.values():
        f.close()

if __name__ == "__main__":
    main()
