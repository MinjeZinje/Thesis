import copy, csv, os, random, numpy as np
from ga import GeneticAlgorithm
from scheduler import Scheduler
from scenario import apply_scenario          # keeps the old ID → flags logic

# ── helper: scheduler that starts each machine with an offset (for downtime) ──
class OffsetScheduler(Scheduler):
    def __init__(self, num_machines, offsets=None):
        super().__init__(num_machines)
        self.offsets = offsets or [0] * num_machines

    def calculate_makespan(self, chromosome):
        machine_available_time = self.offsets[:]          # start with downtime offsets
        job_end_time          = {}

        for (job, op_idx), (m, dur) in chromosome:
            start  = max(machine_available_time[m], job_end_time.get(job, 0))
            finish = start + dur
            machine_available_time[m] = finish
            job_end_time[job]         = finish

        return max(machine_available_time)

# main simulation loop
def simulate_with_rescheduling(instance_data,
                               scenario_id: int,
                               variant_name: str,
                               heuristic_func,
                               max_time: int = 100,
                               noise_std: float = 0.05):
    """
    Fires dynamic events during execution and reschedules after each event.
    Returns a list of (clock_time, makespan).
    """
    clock = 0
    history = []
    name = instance_data["name"]

    data = apply_scenario(copy.deepcopy(instance_data), scenario_id)

    # one-time processing-noise (apply only once at first reschedule)
    if data.get("processing_noise"):
        for job in data["jobs"]:
            for i, (mach, t) in enumerate(job):
                noisy = max(1, int(np.random.normal(t, noise_std * t)))
                job[i] = (mach, noisy)

    # state for breakdowns
    offsets = [0] * data["num_machines"]          # downtime per machine
    breakdowns = data.get("breakdowns", [])

    def current_scheduler():
        return OffsetScheduler(num_machines=data["num_machines"], offsets=offsets)

    ga = GeneticAlgorithm(data)

    # prepare CSV log
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/{name}_{variant_name}_scenario{scenario_id}.csv"
    with open(log_path, "w", newline="") as lf:
        writer = csv.writer(lf)
        writer.writerow(["Time", "Variant", "Instance", "Makespan", "Event"])

        # ---- initial schedule ----
        _, best_mk = ga.run(data, current_scheduler(), heuristic_func)
        writer.writerow([clock, variant_name, name, best_mk, "initial"])
        history.append((clock, best_mk))

        # ---- timeline loop ----
        while clock < max_time:
            clock += 20
            event = "tick"

            # job arrival
            if data.get("arrival_time") == clock:
                new_job = [(0, 3), (2, 5), (1, 4)]
                data["jobs"].append(new_job)
                data["num_jobs"] += 1
                event = "job_arrival"

            # machine breakdowns
            for b in breakdowns:
                if b["start"] == clock:
                    event = f"break_m{b['machine']}"
                    offsets[b["machine"]] = max(offsets[b["machine"]], clock + b["duration"])

            # reschedule
            _, best_mk = ga.run(data, current_scheduler(), heuristic_func)
            writer.writerow([clock, variant_name, name, best_mk, event])
            history.append((clock, best_mk))

    return history
