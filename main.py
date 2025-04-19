# ga_simulation_framework/main.py

from loader import load_instances
from algorithms import run_all_variants

if __name__ == "__main__":
    # Load benchmark data
    instances = load_instances("data.txt")

    # Run all algorithm variants on each selected instance
    for name, data in instances.items():
        data['name'] = name  # Add instance name to data
        print(f"\n--- Running on instance: {name} ---")
        run_all_variants(name, data)
