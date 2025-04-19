# heuristics.py

import random

def random_heuristic(instance_data):
    job_counts = [len(ops) for ops in instance_data['jobs']]
    job_sequence = []
    for job_id, count in enumerate(job_counts):
        job_sequence += [job_id] * count
    random.shuffle(job_sequence)
    return job_sequence

def kk_heuristic(instance_data):
    return random_heuristic(instance_data)  # Placeholder

def spt_heuristic(instance_data):
    return random_heuristic(instance_data)  # Placeholder

def lpt_heuristic(instance_data):
    return random_heuristic(instance_data)  # Placeholder

def srpt_heuristic(instance_data):
    return random_heuristic(instance_data)  # Placeholder

def lrpt_heuristic(instance_data):
    return random_heuristic(instance_data)  # Placeholder

def mixed_heuristic(instance_data):
    heuristics = [kk_heuristic, spt_heuristic, lpt_heuristic, srpt_heuristic, lrpt_heuristic]
    selected = random.choice(heuristics)
    return selected(instance_data)
