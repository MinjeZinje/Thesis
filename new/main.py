import os, csv, copy, statistics
from loader      import load_instances
from heuristics  import HEURISTICS
from ga          import GeneticAlgorithm, run_tabu_search
from rescheduler import simulate_with_rescheduling
from scheduler   import Scheduler
from tqdm        import trange

REPS = 20
SCENARIOS = {"Static": 0, "New Job": 1, "Breakdown": 2, "Time Noise": 3, "Mixed": 4}

# --------------------------------------------------
def run_static_once(inst_data, h_fun):
    """One GA call with a *large* budget for the static case only."""
    ga     = GeneticAlgorithm(inst_data,
                              pop_size=60,
                              num_generations=120,
                              local_search_swaps=15)          # <─ stronger intensification
    sched  = Scheduler(num_machines=inst_data["num_machines"])
    _, mk  = ga.run(inst_data, sched, h_fun)
    return mk
# --------------------------------------------------

def main():
    instances = load_instances("data.txt")

    for scen, sid in SCENARIOS.items():
        out = f"results_{scen.lower().replace(' ', '_')}.csv"
        if os.path.exists(out):
            os.remove(out)

        for inst_name, inst in instances.items():
            inst["name"] = inst_name

            # -------- GA-based variants ----------
            for vname, h_fun in HEURISTICS.items():
                scores = []
                desc   = f"{vname} on {inst_name} | {scen}"
                for _ in trange(REPS, desc=desc, leave=False):
                    data = copy.deepcopy(inst)

                    if sid == 0:                            # static
                        mk = run_static_once(data, h_fun)
                    else:                                   # dynamic
                        mk = simulate_with_rescheduling(data, sid,
                                                       vname, h_fun,
                                                       max_time=100)[-1][1]
                    scores.append(mk)
                    csv.writer(open(out, "a", newline="")).writerow(
                        [inst_name, vname, mk, sid])

                print(f"{vname:5}: avg {statistics.mean(scores):.2f} "
                      f"std {statistics.pstdev(scores):.2f}")

            # -------- Tabu-Search baseline --------
            ts_scores = []
            for _ in trange(REPS, desc=f"TS on {inst_name} | {scen}", leave=False):
                ts_scores.append(
                    run_tabu_search(copy.deepcopy(inst), inst_name, out, sid)[0][2]
                )
            print(f"TS   : avg {statistics.mean(ts_scores):.2f} "
                  f"std {statistics.pstdev(ts_scores):.2f}")

if __name__ == "__main__":
    main()
