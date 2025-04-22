import csv
from ga import GeneticAlgorithm
from scheduler import Scheduler
from heuristics import (
    kk_heuristic, spt_heuristic, lpt_heuristic,
    srpt_heuristic, lrpt_heuristic, mixed_heuristic, random_heuristic
)

def run_all_variants(instance_name, instance_data, results_file="results.csv", scenario_id=0):
    results = []

    results += run_ga_with_heuristic(instance_data, "KK", instance_name, results_file, scenario_id)
    results += run_ga_with_heuristic(instance_data, "SPT", instance_name, results_file, scenario_id)
    results += run_ga_with_heuristic(instance_data, "LPT", instance_name, results_file, scenario_id)
    results += run_ga_with_heuristic(instance_data, "SRPT", instance_name, results_file, scenario_id)
    results += run_ga_with_heuristic(instance_data, "LRPT", instance_name, results_file, scenario_id)
    results += run_ga_with_heuristic(instance_data, "MIXED", instance_name, results_file, scenario_id)
    results += run_ga_with_heuristic(instance_data, "RAND", instance_name, results_file, scenario_id)
    results += run_tabu_search(instance_data, instance_name, results_file, scenario_id)

    return results

def run_ga_with_heuristic(instance_data, heuristic, instance_name, results_file, scenario_id):
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

    # Log result to CSV
    with open(results_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([instance_name, heuristic, best_score, scenario_id])

    return [[instance_name, heuristic, best_score, scenario_id]]

def run_tabu_search(instance_data, instance_name, results_file, scenario_id):
    # Placeholder TS logic
    best_score = 9999  # mock result
    with open(results_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([instance_name, "TS", best_score, scenario_id])
    return [[instance_name, "TS", best_score, scenario_id]]

def get_heuristic_function(name):
    return {
        "KK": kk_heuristic,
        "SPT": spt_heuristic,
        "LPT": lpt_heuristic,
        "SRPT": srpt_heuristic,
        "LRPT": lrpt_heuristic,
        "MIXED": mixed_heuristic,
        "RAND": random_heuristic
    }.get(name, None)
