import random

def random_heuristic(instance_data):
    job_counts = [len(ops) for ops in instance_data['jobs']]
    job_sequence = []
    for job_id, count in enumerate(job_counts):
        job_sequence += [job_id] * count
    random.shuffle(job_sequence)
    return job_sequence

def kk_heuristic(instance_data):
    """
    KK heuristic approximation:
    - Prioritize jobs based on their first operation's processing time (shortest first).
    """
    jobs = instance_data['jobs']
    job_scores = []

    # Look only at the first operation of each job
    for job_id, operations in enumerate(jobs):
        if operations:
            first_op_machine, first_op_time = operations[0]
            job_scores.append((job_id, first_op_time))

    # Sort jobs by ascending first operation processing time
    job_scores.sort(key=lambda x: x[1])

    # Build job sequence: repeat each job ID according to number of operations
    job_sequence = []
    for job_id, _ in job_scores:
        job_sequence.extend([job_id] * len(jobs[job_id]))

    return job_sequence


def spt_heuristic(instance_data):
    """
    Shortest Processing Time (SPT) heuristic:
    - Jobs with lower total processing time are prioritized.
    """
    jobs = instance_data['jobs']
    job_scores = []

    # Calculate total processing time for each job
    for job_id, operations in enumerate(jobs):
        total_time = sum(process_time for _, process_time in operations)
        job_scores.append((job_id, total_time))

    # Sort jobs by ascending total processing time
    job_scores.sort(key=lambda x: x[1])

    # Build job sequence: repeat each job ID according to number of operations
    job_sequence = []
    for job_id, _ in job_scores:
        job_sequence.extend([job_id] * len(jobs[job_id]))

    return job_sequence


def lpt_heuristic(instance_data):
    """
    Longest Processing Time (LPT) heuristic:
    - Jobs with higher total processing time are prioritized first.
    """
    jobs = instance_data['jobs']
    job_scores = []

    # Calculate total processing time for each job
    for job_id, operations in enumerate(jobs):
        total_time = sum(process_time for _, process_time in operations)
        job_scores.append((job_id, total_time))

    # Sort jobs by descending total processing time
    job_scores.sort(key=lambda x: x[1], reverse=True)

    # Build job sequence: repeat each job ID according to number of operations
    job_sequence = []
    for job_id, _ in job_scores:
        job_sequence.extend([job_id] * len(jobs[job_id]))

    return job_sequence


def srpt_heuristic(instance_data):
    """
    Shortest Remaining Processing Time (SRPT) heuristic:
    - Jobs with the least total remaining work are prioritized first.
    (At initial stage, "remaining" = "total", so it's similar to SPT.)
    """
    jobs = instance_data['jobs']
    job_scores = []

    # Calculate total remaining processing time for each job (initial = total)
    for job_id, operations in enumerate(jobs):
        remaining_time = sum(process_time for _, process_time in operations)
        job_scores.append((job_id, remaining_time))

    # Sort jobs by ascending remaining processing time
    job_scores.sort(key=lambda x: x[1])

    # Build job sequence: repeat each job ID according to number of operations
    job_sequence = []
    for job_id, _ in job_scores:
        job_sequence.extend([job_id] * len(jobs[job_id]))

    return job_sequence


def lrpt_heuristic(instance_data):
    """
    Longest Remaining Processing Time (LRPT) heuristic:
    - Jobs with the most total remaining work are prioritized first.
    (At initial stage, "remaining" = "total", same logic as LPT but different name.)
    """
    jobs = instance_data['jobs']
    job_scores = []

    # Calculate total remaining processing time for each job (initial = total)
    for job_id, operations in enumerate(jobs):
        remaining_time = sum(process_time for _, process_time in operations)
        job_scores.append((job_id, remaining_time))

    # Sort jobs by descending remaining processing time
    job_scores.sort(key=lambda x: x[1], reverse=True)

    # Build job sequence: repeat each job ID according to number of operations
    job_sequence = []
    for job_id, _ in job_scores:
        job_sequence.extend([job_id] * len(jobs[job_id]))

    return job_sequence


def mixed_heuristic(instance_data):
    heuristics = [kk_heuristic, spt_heuristic, lpt_heuristic, srpt_heuristic, lrpt_heuristic]
    selected = random.choice(heuristics)
    return selected(instance_data)
