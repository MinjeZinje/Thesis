from __future__ import annotations
from copy import deepcopy
import csv, os, random
from typing import Dict, List, Tuple, Any
from tabu import run_tabu_search
import tempfile
from ga        import GeneticAlgorithm
from scheduler import Scheduler
from scenario  import apply_scenario

def _append_job(data: Dict[str, Any]) -> None:
    new_job = [(0, 3), (2, 5), (1, 4)]
    data["jobs"].append(new_job)
    data["num_jobs"] += 1

def simulate_ts_with_rescheduling(
        instance_data: Dict[str, Any],
        scenario_id:   int,
        max_time:      int = 100,
) -> List[Tuple[int, int]]:
    base          = deepcopy(instance_data)
    scen          = apply_scenario(base, scenario_id)

    events: List[Tuple[int, callable[[], None]]] = []
    if "arrival_time" in scen:
        events.append((scen["arrival_time"],
                       lambda d=scen: _append_job(d)))
    if "breakdowns" in scen:
        for br in scen["breakdowns"]:
            t, m = br["start"], br["machine"]
            events.append((t, lambda d=scen, mm=m: d.setdefault("_broken", set()).add(mm)))
    events.sort()

    def _run_tabu(machine_status: Dict[int, str | float] | None = None) -> int:
        tmp_csv = tempfile.NamedTemporaryFile(delete=False).name
        res  = run_tabu_search(scen, scen["name"], tmp_csv, scenario_id)[0]
        best = res[2]
        seq = None
        if len(res) > 3:
            chrom = res[3]
            if isinstance(chrom, list) and all(isinstance(x, int) for x in chrom):
                ga_stub = GeneticAlgorithm(scen)
                seq = ga_stub._decode(chrom, scen)
            else:
                seq = chrom

        # Final type check - bulletproof against broken Tabu return
        if machine_status and (seq is None or not isinstance(seq, (list, tuple))):
            return best
        if machine_status and seq is not None:
            sched = Scheduler(scen["num_machines"])
            best = sched.calculate_makespan(seq, machine_status)
        return best

    history: List[Tuple[int, int]] = []
    clk = 0
    history.append((clk, _run_tabu()))

    for t, apply_evt in events:
        if t > max_time:
            break
        clk = t
        apply_evt()

        m_stat: Dict[int, str | float] = {}
        if scen.get("processing_noise"):
            factor = 1.1 + random.random() * 0.1
            for mm in range(scen["num_machines"]):
                m_stat[mm] = factor
        if "_broken" in scen:
            for mm in scen["_broken"]:
                m_stat[mm] = "broken"

        history.append((clk, _run_tabu(m_stat)))

    if clk < max_time:
        history.append((max_time, history[-1][1]))
    return history

# ---------- main entry: continuous rescheduling ---
def simulate_with_rescheduling(
    instance_data : Dict[str, Any],
    scenario_id   : int,
    variant_name  : str,
    heuristic_func,
    max_time      : int = 100,
) -> List[Tuple[int, int]]:
    base           = deepcopy(instance_data)
    scenario_data  = apply_scenario(base, scenario_id)

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

    inst_name = instance_data["name"]
    log_fname = f"logs/{inst_name}_{variant_name}_scenario{scenario_id}.csv"
    os.makedirs("logs", exist_ok=True)
    fout   = open(log_fname, "w", newline="")
    writer = csv.writer(fout)
    writer.writerow(["time", "variant", "instance", "makespan", "event"])

    def run_ga_and_log(clk: int, tag: str) -> int:
        m_status: Dict[int, str | float] = {}
        if scenario_data.get("processing_noise"):
            factor = 1.1 + random.random() * 0.1
            for m in range(scenario_data["num_machines"]):
                m_status[m] = factor
        if "_broken" in scenario_data:
            for m in scenario_data["_broken"]:
                m_status[m] = "broken"

        ga = GeneticAlgorithm(
            scenario_data,
            pop_size           = 60,
            num_generations    = 120,
            local_search_swaps = 15,
        )
        sched = Scheduler(scenario_data["num_machines"], use_cache=True)
        best_ind, _ = ga.run(scenario_data, sched, heuristic_func=heuristic_func)
        best_mk = sched.calculate_makespan(
            ga._decode(best_ind, scenario_data),
            machine_status=m_status
        )
        writer.writerow([clk, variant_name, inst_name, best_mk, tag])
        return best_mk

    history: List[Tuple[int, int]] = []
    clk = 0
    history.append((clk, run_ga_and_log(clk, "initial")))

    while next_evt is not None:
        evt_time, apply_evt, evt_name = next_evt
        if evt_time > max_time:
            break
        clk = evt_time
        apply_evt()
        history.append((clk, run_ga_and_log(clk, evt_name)))
        next_evt = next(agenda_iter, None)

    if clk < max_time:
        clk = max_time
        history.append((clk, run_ga_and_log(clk, "finish")))

    fout.close()
    return history
