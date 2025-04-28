import csv
import random
from copy import deepcopy
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
        pop_size=100,  # bigger population
        num_generations=200,  # more generations
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
    from scheduler import Scheduler

    # Parameters
    max_iters = 100
    tabu_size = 10

    scheduler = Scheduler(num_machines=instance_data['num_machines'])

    # Create initial random solution
    def random_solution(instance_data):
        job_counts = [len(ops) for ops in instance_data['jobs']]
        job_sequence = []
        for job_id, count in enumerate(job_counts):
            job_sequence += [job_id] * count
        random.shuffle(job_sequence)
        return job_sequence

    def decode(individual, instance_data):
        job_op_indices = [0] * instance_data['num_jobs']
        operation_sequence = []
        for job_id in individual:
            op_idx = job_op_indices[job_id]
            machine, time = instance_data['jobs'][job_id][op_idx]
            operation_sequence.append(((job_id, op_idx), (machine, time)))
            job_op_indices[job_id] += 1
        return operation_sequence

    # Evaluate a solution
    def evaluate(individual):
        decoded = decode(individual, instance_data)
        return scheduler.calculate_makespan(decoded)

    # Neighborhood generation: simple 2-position swap
    def get_neighbors(solution):
        neighbors = []
        for _ in range(10):  # limit number of neighbors generated
            neighbor = solution.copy()
            i, j = random.sample(range(len(solution)), 2)
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
            neighbors.append((neighbor, (i, j)))
        return neighbors

    # Initialize
    current = random_solution(instance_data)
    current_score = evaluate(current)
    best = deepcopy(current)
    best_score = current_score
    tabu_list = []

    for _ in range(max_iters):
        neighbors = get_neighbors(current)
        neighbors = sorted(neighbors, key=lambda x: evaluate(x[0]))

        for neighbor, move in neighbors:
            if move not in tabu_list:
                current = neighbor
                current_score = evaluate(current)
                tabu_list.append(move)
                if len(tabu_list) > tabu_size:
                    tabu_list.pop(0)
                break

        if current_score < best_score:
            best = deepcopy(current)
            best_score = current_score

    # Save result
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
