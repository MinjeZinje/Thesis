# tabu.py
import random, csv
from copy import deepcopy
from scheduler import Scheduler


def _random_solution(jobs):
    seq = [jid for jid, ops in enumerate(jobs) for _ in ops]
    random.shuffle(seq)
    return seq


def _decode(sol, jobs):
    idx = [0] * len(jobs)
    out = []
    for jid in sol:
        m, t = jobs[jid][idx[jid]]
        out.append(((jid, idx[jid]), (m, t)))
        idx[jid] += 1
    return out


def run_tabu_search(instance, inst_name, csv_path, scenario_id,
                    max_iters=250, tabu_size=15):
    """Returns [[instance, 'TS', best_mk, scenario_id]] and writes to csv."""
    jobs, nm = instance["jobs"], instance["num_machines"]
    sched = Scheduler(nm)

    cur = _random_solution(jobs)
    best = cur[:]
    best_mk = sched.calculate_makespan(_decode(best, jobs))

    tabu = []                      # store swapped index-pairs
    for _ in range(max_iters):
        #  generate 10 neighbours by random 2-swap
        neigh = []
        for _ in range(10):
            n = cur[:]
            i, j = random.sample(range(len(n)), 2)
            n[i], n[j] = n[j], n[i]
            neigh.append((n, (i, j)))

        #  pick first admissible improvement
        neigh.sort(key=lambda x: sched.calculate_makespan(_decode(x[0], jobs)))
        for sol, move in neigh:
            if move not in tabu:
                cur = sol
                tabu.append(move)
                if len(tabu) > tabu_size:
                    tabu.pop(0)
                mk = sched.calculate_makespan(_decode(cur, jobs))
                if mk < best_mk:
                    best_mk, best = mk, cur[:]
                break

    #  write exactly one line (best run) to the csv expected by main.py
    with open(csv_path, "a", newline="") as f:
        csv.writer(f).writerow([inst_name, "TS", best_mk, scenario_id])

    return [[inst_name, "TS", best_mk, scenario_id]]
