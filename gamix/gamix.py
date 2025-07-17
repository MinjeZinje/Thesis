from __future__ import annotations
import os, csv, copy, statistics, random
from typing import Dict
from multiprocessing import Pool
import pandas as pd
from tqdm import tqdm

from loader import load_instances
from heuristics import HEURISTICS
from ga import GeneticAlgorithm
from scheduler import Scheduler
from rescheduler import simulate_with_rescheduling

random.seed(42)
REPS = 10
SCENARIOS: Dict[str, int] = {
    "Static": 0,
    "NewJob": 1,
    "Breakdown": 2,
    "TimeNoise": 3,
    "Mixed": 4,
}

def _ga_once(inst: dict, sid: int, hfun) -> int:
    data = copy.deepcopy(inst)
    if sid == 0:
        ga = GeneticAlgorithm(data)
        sched = Scheduler(num_machines=data["num_machines"])
        return ga.run(data, sched, hfun)[1]
    hist = simulate_with_rescheduling(
        data, scenario_id=sid,
        variant_name=hfun.__name__,
        heuristic_func=hfun,
        max_time=100,
    )
    return hist[-1][1]

def main() -> None:
    instances = load_instances("data.txt")
    os.makedirs("results", exist_ok=True)
    rows = []
    total = len(instances) * len(SCENARIOS) * len(HEURISTICS)
    with tqdm(total=total) as pbar:
        for inst in instances:
            for scen_name, sid in SCENARIOS.items():
                for hname, hfun in HEURISTICS.items():
                    with Pool() as pool:
                        mks = pool.starmap(
                            _ga_once, [(inst, sid, hfun)] * REPS
                        )
                    rows.append([inst["name"], scen_name, hname,
                                 statistics.mean(mks)])
                    pbar.update(1)

    with open("results/summary.csv", "w", newline="") as f:
        csv.writer(f).writerows(
            [["Instance", "Scenario", "Algorithm", "MeanMakespan"], *rows]
        )

    df = pd.read_csv("results/summary.csv")
    pivot = df.pivot_table(index=["Instance", "Scenario"],
                           columns="Algorithm", values="MeanMakespan")
    (pivot.subtract(pivot["GAMIX"], axis=0)
          .to_csv("results/delta_vs_gamix.csv"))

if __name__ == "__main__":
    main()
