# algorithms.py
import csv
import os
from ga import GeneticAlgorithm
from scheduler import Scheduler
from heuristics import (
    kk_heuristic, spt_heuristic, lpt_heuristic,
    srpt_heuristic, lrpt_heuristic, mixed_heuristic
)


def run_all_variants(instance_name, instance_data):
    print(f"Running GAKK on {instance_name}")
    run_ga_with_heuristic(instance_data, heuristic="KK")

    print(f"Running GASPT on {instance_name}")
    run_ga_with_heuristic(instance_data, heuristic="SPT")

    print(f"Running GALPT on {instance_name}")
    run_ga_with_heuristic(instance_data, heuristic="LPT")

    print(f"Running GASRPT on {instance_name}")
    run_ga_with_heuristic(instance_data, heuristic="SRPT")

    print(f"Running GALRPT on {instance_name}")
    run_ga_with_heuristic(instance_data, heuristic="LRPT")

    print(f"Running GAM (mixed) on {instance_name}")
    run_ga_with_heuristic(instance_data, heuristic="MIXED")

    print(f"Running GA (standard) on {instance_name}")
    run_ga_with_heuristic(instance_data, heuristic=None)

    print(f"Running TS (Tabu Search) on {instance_name}")
    run_tabu_search(instance_data)


def run_ga_with_heuristic(instance_data, heuristic):
    ga = GeneticAlgorithm(
        pop_size=30,
        num_generations=50,
        crossover_rate=0.8,
        mutation_rate=0.2,
        elitism_rate=0.1
    )

    scheduler = Scheduler(num_machines=instance_data['num_machines'])
    heuristic_func = get_heuristic_function(heuristic)

    best_sol, best_score = ga.run(instance_data, scheduler, heuristic_func)
    print(f"[{heuristic or 'Standard GA'}] Best Makespan: {best_score}")

    # Save to results.csv
    file_exists = os.path.isfile("results.csv")
    with open("results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Instance", "Algorithm", "Makespan"])
        writer.writerow([instance_data.get('name', 'Unknown'), heuristic or 'Standard GA', best_score])


def run_tabu_search(instance_data):
    print("[TS] Tabu Search placeholder... (not implemented)")


def get_heuristic_function(name):
    if name == "KK":
        return kk_heuristic
    elif name == "SPT":
        return spt_heuristic
    elif name == "LPT":
        return lpt_heuristic
    elif name == "SRPT":
        return srpt_heuristic
    elif name == "LRPT":
        return lrpt_heuristic
    elif name == "MIXED":
        return mixed_heuristic
    return None
