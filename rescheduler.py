from __future__ import annotations
from copy import deepcopy
import csv, os
from typing import Dict, List, Tuple, Any

from ga import GeneticAlgorithm
from scheduler import Scheduler
from scenario import apply_scenario


def _append_job(data: Dict[str, Any]) -> None:
    """A tiny helper that injects ONE synthetic 3-op job (same as before)."""
    new_job = [(0, 3), (2, 5), (1, 4)]
    data["jobs"].append(new_job)
    data["num_jobs"] += 1


def simulate_with_rescheduling(
    instance_data: Dict[str, Any],
    scenario_id: int,
    variant_name: str,
    heuristic_func,
    max_time: int = 100,
) -> List[Tuple[int, int]]:
    """
    Returns
    -------
    list[(time, makespan)]
        History of (simulation-clock, best makespan) pairs.
    """
    base = deepcopy(instance_data)
    scenario_data = apply_scenario(base, scenario_id)

    # Collect “event agenda” 
    # Each item -> (event_time, callable_to_apply, human_name)
    agenda: List[Tuple[int, callable[[], None], str]] = []

    if "arrival_time" in scenario_data:
        t = scenario_data["arrival_time"]
        agenda.append((t, lambda d=scenario_data: _append_job(d), "job_arrival"))

    if "breakdowns" in scenario_data:
        for b in scenario_data["breakdowns"]:
            t = b["start"]
            mach = b["machine"]

            def _mk_break(d=scenario_data, m=mach):
                # **placeholder** – real breakdown logic could disable op on m
                d.setdefault("_broken", set()).add(m)

            agenda.append((t, _mk_break, f"breakdown_m{mach}"))

    agenda.sort(key=lambda x: x[0])               # chronological order
    agenda_iter = iter(agenda)
    next_evt = next(agenda_iter, None)


    inst_name = instance_data["name"]
    log_fname = f"logs/{inst_name}_{variant_name}_scenario{scenario_id}.csv"
    os.makedirs("logs", exist_ok=True)
    fout = open(log_fname, "w", newline="")
    writer = csv.writer(fout)
    writer.writerow(["time", "variant", "instance", "makespan", "event"])


    def run_ga_and_log(clk: int, tag: str) -> int:
        ga = GeneticAlgorithm(
            scenario_data,
            pop_size=60,
            num_generations=120,
            local_search_swaps=15,
        )
        sched = Scheduler(scenario_data["num_machines"], use_cache=True)
        _, best = ga.run(scenario_data, sched, heuristic_func)
        writer.writerow([clk, variant_name, inst_name, best, tag])
        return best

    history: List[Tuple[int, int]] = []

    # Initial scheduling 
    clk = 0
    history.append((clk, run_ga_and_log(clk, "initial")))

    # Main loop 
    while True:
        # No more events?  We’re done.
        if next_evt is None:
            break

        evt_time, apply_evt, evt_name = next_evt

        # If the next event is beyond our horizon, stop early.
        if evt_time > max_time:
            break

        # Advance clock to the event
        clk = evt_time
        apply_evt()                            # mutate scenario_data in-place
        history.append((clk, run_ga_and_log(clk, evt_name)))

        # Fetch next event
        next_evt = next(agenda_iter, None)

    # Final call at horizon 
    if clk < max_time:
        clk = max_time
        history.append((clk, run_ga_and_log(clk, "finish")))

    fout.close()
    return history
