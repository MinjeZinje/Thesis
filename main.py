from loader import load_instances
from algorithms import run_all_variants
import csv

SCENARIOS = {
    "scenario1": 1,
    "scenario2": 2,
    "scenario3": 3,
    "scenario4": 4,
}

if __name__ == "__main__":
    instances = load_instances("data.txt")

    for scenario_name, scenario_id in SCENARIOS.items():
        print(f"\n=== Running {scenario_name.upper()} ===")

        output_file = f"results_{scenario_name}.csv"
        results = []

        for name, data in instances.items():
            print(f"\n--- Running on instance: {name} ---")
            data['name'] = name
            result_rows = run_all_variants(name, data, results_file=output_file, scenario_id=scenario_id)
            results.extend(result_rows)

        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Instance", "Variant", "Best Makespan", "Scenario"])
            writer.writerows(results)

        print(f" Saved results to {output_file}")
