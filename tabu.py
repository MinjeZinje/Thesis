import random
import csv
from copy import deepcopy
from scheduler import Scheduler

def _random_solution(jobs):
    """Create a random job‐based permutation (one entry per operation)."""
    seq = [jid for jid, ops in enumerate(jobs) for _ in ops]
    random.shuffle(seq)
    return seq

def _decode(sol, jobs):
    """
    Translate a job‐sequence (e.g. [0,2,1,0,2,1,…]) into an operation list
    [ ((job_id, op_idx), (mach, dur)), … ] for the scheduler.
    """
    idx = [0] * len(jobs)
    out = []
    for jid in sol:
        m, t = jobs[jid][idx[jid]]
        out.append(((jid, idx[jid]), (m, t)))
        idx[jid] += 1
    return out

def run_tabu_search(
    instance_data,
    inst_name: str,
    csv_path: str,
    scenario_id: int,
    machine_status: dict | None = None,
    max_iters: int = 250,
    tabu_size: int = 15
) -> list[list]:
    """
    Tabu Search that respects broken machines / noise.
    - instance_data: dict with "jobs" and "num_machines"
    - machine_status: { machine_id: "broken" | float multiplier }
    Returns [[inst_name, "TS", best_mk, scenario_id, best_seq]]
    and appends one line to csv_path for the best makespan.
    """
    jobs = instance_data["jobs"]
    nm = instance_data["num_machines"]
    sched = Scheduler(nm, use_cache=True)

    # Initial random solution
    cur = _random_solution(jobs)
    best = cur[:]
    # Evaluate initial
    init_ops = _decode(best, jobs)
    best_mk = sched.calculate_makespan(init_ops, machine_status=machine_status)

    tabu = []
    for _ in range(max_iters):
        # Generate neighbors by swapping two positions
        neighbors = []
        for _ in range(10):
            candidate = cur[:]
            i, j = random.sample(range(len(candidate)), 2)
            candidate[i], candidate[j] = candidate[j], candidate[i]
            neighbors.append((candidate, (i, j)))

        # Evaluate all neighbors under current machine_status
        scored = []
        for cand, move in neighbors:
            ops = _decode(cand, jobs)
            mk = sched.calculate_makespan(ops, machine_status=machine_status)
            scored.append((mk, cand, move))
        scored.sort(key=lambda x: x[0])

        # Pick the first admissible move
        for mk, cand, move in scored:
            if move not in tabu:
                cur = cand
                tabu.append(move)
                if len(tabu) > tabu_size:
                    tabu.pop(0)
                if mk < best_mk:
                    best_mk = mk
                    best = cand[:]
                break

    # Final decode and (re-)evaluation under machine_status
    best_ops = _decode(best, jobs)
    final_mk = sched.calculate_makespan(best_ops, machine_status=machine_status)

    # Log to CSV
    with open(csv_path, "a", newline="") as f:
        csv.writer(f).writerow([inst_name, "TS", final_mk, scenario_id])

    return [[inst_name, "TS", final_mk, scenario_id, best_ops]]
