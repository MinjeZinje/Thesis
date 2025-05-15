import os
import csv
from loader import load_instances
from scenario import apply_scenario
from scheduler import Scheduler
from heuristics import HEURISTICS
from ga import GeneticAlgorithm, run_tabu_search
from tqdm import trange

REPS = 20

SCENARIOS = {
    "Static": 0,
    "New Job": 1,
    "Breakdown": 2,
    "Time Noise": 3,
    "Mixed": 4
}

def simulate_with_rescheduling(ga, instance_data, scheduler, heuristic_func,
                               reps, instance_name, variant_name,
                               scenario_id, output_file):
    best_scores = []
    for rep in trange(reps, desc=f"{variant_name} on {instance_name}"):
        instance_copy = {
            "jobs": [list(job) for job in instance_data["jobs"]],
            "num_jobs": instance_data["num_jobs"],
            "num_machines": instance_data["num_machines"]
        }

        updated_data = apply_scenario(instance_copy, scenario_id)
        best_solution, best_score = ga.run(updated_data, scheduler, heuristic_func)
        best_scores.append(best_score)

        with open(output_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([instance_name, variant_name, best_score, scenario_id])

    return best_scores

def main():
    instances = load_instances("data.txt")

    for scenario_name, scenario_id in SCENARIOS.items():
        print(f"\n=== Running {scenario_name.upper()} ===")
        output_file = f"results_{scenario_name.lower()}.csv"

        if os.path.exists(output_file):
            os.remove(output_file)

        for name, data in instances.items():
            print(f"\n--- Running on instance: {name} ---")
            data['name'] = name

            for variant_name, heuristic_func in HEURISTICS.items():
                print(f"Running variant: {variant_name}")
                ga = GeneticAlgorithm(instance_data=data)
                scheduler = Scheduler(num_machines=data['num_machines'])

                scores = simulate_with_rescheduling(
                    ga, data, scheduler, heuristic_func,
                    REPS, name, variant_name, scenario_id, output_file
                )

                avg_score = sum(scores) / len(scores)
                std_dev = (sum([(x - avg_score) ** 2 for x in scores]) / len(scores)) ** 0.5
                print(f"→ {variant_name} Avg: {avg_score:.2f}, Std: {std_dev:.2f}")

            # Run TS 20 times
            print("Running variant: TS")
            ts_scores = []
            for rep in trange(REPS, desc=f"TS on {name}"):
                ts_row = run_tabu_search(data, name, output_file, scenario_id)
                ts_scores.append(ts_row[0][2])  # extract makespan

            ts_avg = sum(ts_scores) / len(ts_scores)
            ts_std = (sum((x - ts_avg) ** 2 for x in ts_scores) / len(ts_scores)) ** 0.5
            print(f"→ TS Avg: {ts_avg:.2f}, Std: {ts_std:.2f}")

if __name__ == "__main__":
    main()
