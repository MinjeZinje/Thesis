from __future__ import annotations
from copy import deepcopy
import csv, os, random
from typing import Dict, List, Tuple, Any

from ga        import GeneticAlgorithm
from scheduler import Scheduler
from scenario  import apply_scenario


# ---------- tiny helper: new-job arrival ----------
def _append_job(data: Dict[str, Any]) -> None:
    """Inject one synthetic 3-operation job on machines 0-2-1."""
    new_job = [(0, 3), (2, 5), (1, 4)]
    data["jobs"].append(new_job)
    data["num_jobs"] += 1


# ---------- main entry: continuous rescheduling ---
def simulate_with_rescheduling(
    instance_data : Dict[str, Any],
    scenario_id   : int,
    variant_name  : str,
    heuristic_func,
    max_time      : int = 100,
) -> List[Tuple[int, int]]:
    """
    Returns
    -------
    list[(time, makespan)]   # history of GA best values
    """
    base           = deepcopy(instance_data)
    scenario_data  = apply_scenario(base, scenario_id)

    # ---- build agenda of dynamic events ----------------
    agenda: List[Tuple[int, callable[[], None], str]] = []

    if "arrival_time" in scenario_data:
        t = scenario_data["arrival_time"]
        agenda.append((t, lambda d=scenario_data: _append_job(d), "job_arrival"))

    if "breakdowns" in scenario_data:
        for b in scenario_data["breakdowns"]:
            t, mach = b["start"], b["machine"]

            def _mk_break(d=scenario_data, m=mach):
                d.setdefault("_broken", set()).add(m)

            agenda.append((t, _mk_break, f"breakdown_m{mach}"))

    agenda.sort(key=lambda x: x[0])
    agenda_iter = iter(agenda)
    next_evt    = next(agenda_iter, None)

    # ---- log file --------------------------------------
    inst_name = instance_data["name"]
    log_fname = f"logs/{inst_name}_{variant_name}_scenario{scenario_id}.csv"
    os.makedirs("logs", exist_ok=True)
    fout   = open(log_fname, "w", newline="")
    writer = csv.writer(fout)
    writer.writerow(["time", "variant", "instance", "makespan", "event"])

    # ---- helper to run GA + log ------------------------

    def run_ga_and_log(clk: int, tag: str) -> int:
        # derive machine-status dict for this moment
        m_status: Dict[int, str | float] = {}
        if scenario_data.get("processing_noise"):
            factor = 1.1 + random.random() * 0.1          # 10–20 % noise
            for m in range(scenario_data["num_machines"]):
                m_status[m] = factor
        if "_broken" in scenario_data:
            for m in scenario_data["_broken"]:
                m_status[m] = "broken"

        # --- run GA (fitness evals ignore status) --------
        ga = GeneticAlgorithm(
            scenario_data,
            pop_size           = 60,
            num_generations    = 120,
            local_search_swaps = 15,
        )
        sched = Scheduler(scenario_data["num_machines"], use_cache=True)

        best_ind, _ = ga.run(scenario_data, sched, heuristic_func=heuristic_func)

        # --- re-score best individual with current machine_status ---
        best_mk = sched.calculate_makespan(
            ga._decode(best_ind, scenario_data),
            machine_status=m_status
        )

        writer.writerow([clk, variant_name, inst_name, best_mk, tag])
        return best_mk

    # ---- simulation loop -------------------------------
    history: List[Tuple[int, int]] = []
    clk = 0
    history.append((clk, run_ga_and_log(clk, "initial")))

    while next_evt is not None:
        evt_time, apply_evt, evt_name = next_evt
        if evt_time > max_time:
            break

        clk = evt_time
        apply_evt()                                    # mutate scenario_data
        history.append((clk, run_ga_and_log(clk, evt_name)))
        next_evt = next(agenda_iter, None)

    if clk < max_time:                                # final evaluation at horizon
        clk = max_time
        history.append((clk, run_ga_and_log(clk, "finish")))

    fout.close()
    return history
