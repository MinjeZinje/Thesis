# main.py
import os, csv, copy, statistics
from loader      import load_instances
from heuristics  import HEURISTICS
from ga          import GeneticAlgorithm
from rescheduler import simulate_with_rescheduling
from scheduler   import Scheduler
from tqdm        import trange
from tabu        import run_tabu_search          # ← NEW

REPS = 20
SCENARIOS = {"Static": 0, "New Job": 1, "Breakdown": 2,
             "Time Noise": 3, "Mixed": 4}


def run_static_once(data, heuristic):
    """One larger-budget GA call for the static case."""
    ga    = GeneticAlgorithm(data,
                             pop_size=60,
                             num_generations=120,
                             local_search_swaps=15)
    sched = Scheduler(num_machines=data["num_machines"])
    _, mk = ga.run(data, sched, heuristic)
    return mk


def main():
    instances = load_instances("data.txt")

    for scen_name, sid in SCENARIOS.items():
        out_csv = f"results_{scen_name.lower().replace(' ', '_')}.csv"
        if os.path.exists(out_csv):
            os.remove(out_csv)

        for inst_name, inst_data in instances.items():
            inst_data["name"] = inst_name

            # ---------- GA family ----------
            for vname, hfun in HEURISTICS.items():
                scores = []
                desc   = f"{vname} on {inst_name} | {scen_name}"
                for _ in trange(REPS, desc=desc, leave=False):
                    data_cp = copy.deepcopy(inst_data)
                    if sid == 0:        # static
                        mk = run_static_once(data_cp, hfun)
                    else:               # dynamic
                        mk = simulate_with_rescheduling(
                                data_cp, sid, vname, hfun,
                                max_time=100)[-1][1]
                    scores.append(mk)
                    csv.writer(open(out_csv, "a", newline=""))\
                       .writerow([inst_name, vname, mk, sid])

                print(f"{vname:5}: avg {statistics.mean(scores):.2f}  "
                      f"std {statistics.pstdev(scores):.2f}")

            # ---------- Tabu baseline ----------
            ts_scores = []
            for _ in trange(REPS, desc=f"TS on {inst_name} | {scen_name}", leave=False):
                res = run_tabu_search(copy.deepcopy(inst_data),
                                      inst_name, out_csv, sid)
                ts_scores.append(res[0][2])

            print(f"TS   : avg {statistics.mean(ts_scores):.2f}  "
                  f"std {statistics.pstdev(ts_scores):.2f}")


if __name__ == "__main__":
    main()
