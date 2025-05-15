from copy import deepcopy
from ga import GeneticAlgorithm
from scheduler import Scheduler
from scenario import apply_scenario
import csv
import os


def simulate_with_rescheduling(instance_data, scenario_id, variant_name, heuristic_func, max_time=100):
    """
    Main loop for dynamic event handling with continuous rescheduling.
    """
    clock = 0
    history = []
    instance_name = instance_data['name']

    scenario_data = apply_scenario(instance_data, scenario_id)
    scheduler = Scheduler(num_machines=scenario_data['num_machines'])
    ga = GeneticAlgorithm(scenario_data)

    # Prepare output directory
    log_path = f"logs/{instance_name}_{variant_name}_scenario{scenario_id}.csv"
    os.makedirs("logs", exist_ok=True)
    with open(log_path, 'w', newline='') as logfile:
        writer = csv.writer(logfile)
        writer.writerow(["Time", "Variant", "Instance", "Makespan", "Event"])

        # Initial scheduling
        best_sol, best_makespan = ga.run(scenario_data, scheduler, heuristic_func)
        writer.writerow([clock, variant_name, instance_name, best_makespan, "initial"])
        history.append((clock, best_makespan))

        # Simulate over time
        while clock <= max_time:

            event = "reschedule"
            # Check for job arrivals
            if 'arrival_time' in scenario_data and clock == scenario_data['arrival_time']:
                print(f"[Time {clock}] New job arrived. Re-running GA...")
                new_job = [(0, 3), (2, 5), (1, 4)]
                scenario_data['jobs'].append(new_job)
                scenario_data['num_jobs'] += 1
                event = "job_arrival"

            # Check for breakdowns
            if 'breakdowns' in scenario_data:
                for b in scenario_data['breakdowns']:
                    if b['start'] == clock:
                        print(f"[Time {clock}] Machine {b['machine']} broke down for {b['duration']}.")
                        event = f"breakdown_m{b['machine']}"
                        # Could add actual delay logic later

            # Re-run GA
            best_sol, best_makespan = ga.run(scenario_data, scheduler, heuristic_func)
            writer.writerow([clock, variant_name, instance_name, best_makespan, event])
            history.append((clock, best_makespan))

            clock += 10

    return history
