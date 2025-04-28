from loader import load_instances
from algorithms import run_all_variants
import csv

SCENARIOS = {
    "Static": 0,
    "Scenario1": 1,
    "Scenario2": 2,
    "Scenario3": 3,
    "Scenario4": 4,
}

if __name__ == "__main__":
    instances = load_instances("data.txt")

    for scenario_name, scenario_id in SCENARIOS.items():
        print(f"\n=== Running {scenario_name.upper()} ===")

        output_file = (
            "results.csv" if scenario_name == "Static" else f"results_{scenario_name.lower()}.csv"
        )

        results = []

        for name, data in instances.items():
            print(f"\n--- Running on instance: {name} ---")
            data['name'] = name

            if scenario_id == 0:
                modified_data = data  # no dynamic change
            else:
                from scenario import apply_scenario
                modified_data = apply_scenario(data, scenario_id)

            result_rows = run_all_variants(name, modified_data, results_file=output_file, scenario_id=scenario_id)
            results.extend(result_rows)

        # Write results
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Instance", "Variant", "Best Makespan", "Scenario"])
            writer.writerows(results)

        print(f" Saved results to {output_file}")
