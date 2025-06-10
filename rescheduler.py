from __future__ import annotations
from copy import deepcopy
import csv, os, random, tempfile
from typing import Dict, List, Tuple, Any

from tabu       import run_tabu_search
from ga         import GeneticAlgorithm
from scheduler  import Scheduler
from scenario   import apply_scenario

def _append_job(data: Dict[str, Any]) -> None:
    data["jobs"].append([(0, 3), (2, 5), (1, 4)])
    data["num_jobs"] += 1

def simulate_ts_with_rescheduling(
    instance_data: Dict[str, Any],
    scenario_id  : int,
    max_time     : int = 100
) -> List[Tuple[int,int]]:
    inst_copy = deepcopy(instance_data)
    scen      = apply_scenario(inst_copy, scenario_id)
    sched     = Scheduler(scen["num_machines"], use_cache=True)

    # build events
    events: List[Tuple[int, callable[[],None]]] = []
    if "arrival_time" in scen:
        events.append((scen["arrival_time"], lambda d=scen: _append_job(d)))
    if "breakdowns" in scen:
        for br in scen["breakdowns"]:
            t, dur, m = br["start"], br["duration"], br["machine"]
            events.append((t,     lambda d=scen, mm=m: d.setdefault("_broken", set()).add(mm)))
            events.append((t+dur, lambda d=scen, mm=m: d["_broken"].remove(mm)))
    events.sort(key=lambda x: x[0])

    def _run_tabu(machine_status: Dict[int,Any] | None = None) -> int:
        tmp_csv = tempfile.NamedTemporaryFile(delete=False).name
        res     = run_tabu_search(
            scen, scen["name"], tmp_csv, scenario_id,
            machine_status=machine_status
        )[0]
        best_mk = res[2]
        if len(res) > 4 and res[4] is not None:
            seq = res[4]
            # already decoded?
            if seq and isinstance(seq[0], tuple) and isinstance(seq[0][1], tuple):
                op_seq = seq
            else:
                op_seq = GeneticAlgorithm(scen)._decode(seq, scen)
            best_mk = sched.calculate_makespan(op_seq, machine_status=machine_status)
        return best_mk

    history: List[Tuple[int,int]] = []
    clk = 0
    history.append((0, _run_tabu(None)))

    for t, apply_evt in events:
        if t > max_time:
            break
        clk = t
        apply_evt()
        m_stat: Dict[int,Any] = {}
        if scen.get("processing_noise"):
            fac = 1.1 + random.random()*0.1
            for mm in range(scen["num_machines"]):
                m_stat[mm] = fac
        if "_broken" in scen:
            for mm in scen["_broken"]:
                m_stat[mm] = "broken"
        history.append((clk, _run_tabu(m_stat)))

    if clk < max_time:
        m_stat = {}
        if scen.get("processing_noise"):
            fac = 1.1 + random.random()*0.1
            for mm in range(scen["num_machines"]):
                m_stat[mm] = fac
        if "_broken" in scen:
            for mm in scen["_broken"]:
                m_stat[mm] = "broken"
        history.append((max_time, _run_tabu(m_stat)))

    return history


def simulate_with_rescheduling(
    instance_data : Dict[str, Any],
    scenario_id   : int,
    variant_name  : str,
    heuristic_func,
    max_time      : int = 100
) -> List[Tuple[int,int]]:
    inst_copy    = deepcopy(instance_data)
    scen         = apply_scenario(inst_copy, scenario_id)
    sched_default = Scheduler(scen["num_machines"], use_cache=True)

    # build agenda
    agenda: List[Tuple[int, callable[[],None], str]] = []
    if "arrival_time" in scen:
        agenda.append((scen["arrival_time"], lambda d=scen: _append_job(d), "job_arrival"))
    if "breakdowns" in scen:
        for br in scen["breakdowns"]:
            t, dur, m = br["start"], br["duration"], br["machine"]
            agenda.append((t,     lambda d=scen, mm=m: d.setdefault("_broken", set()).add(mm), f"br_start_m{m}"))
            agenda.append((t+dur, lambda d=scen, mm=m: d["_broken"].remove(mm),                 f"br_end_m{m}"))
    agenda.sort(key=lambda x: x[0])
    it = iter(agenda)
    next_evt = next(it, None)

    # prepare log
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{instance_data['name']}_{variant_name}_sc{scenario_id}.csv"
    writer   = csv.writer(open(log_path, "w", newline=""))
    writer.writerow(["time","variant","instance","makespan","event"])

    def _run_ga(clk: int, tag: str) -> int:
        m_stat: Dict[int,Any] = {}
        if scen.get("processing_noise"):
            fac = 1.1 + random.random()*0.1
            for mm in range(scen["num_machines"]):
                m_stat[mm] = fac
        if "_broken" in scen:
            for mm in scen["_broken"]:
                m_stat[mm] = "broken"

        ga = GeneticAlgorithm(scen, pop_size=60, num_generations=120, local_search_swaps=15)
        best, _ = ga.run(scen, sched_default, heuristic_func)
        op_seq = ga._decode(best, scen)
        mk = sched_default.calculate_makespan(op_seq, machine_status=m_stat)
        writer.writerow([clk, variant_name, instance_data["name"], mk, tag])
        return mk

    history: List[Tuple[int,int]] = []
    clk = 0
    history.append((0, _run_ga(0, "initial")))

    while next_evt and next_evt[0] <= max_time:
        t, fn, tag = next_evt
        clk = t
        fn()
        history.append((clk, _run_ga(clk, tag)))
        next_evt = next(it, None)

    if clk < max_time:
        clk = max_time
        history.append((clk, _run_ga(clk, "finish")))

    return history
