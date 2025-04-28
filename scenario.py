# scenario.py

import copy
import random
import numpy as np

def apply_scenario(instance_data, scenario_id):
    if scenario_id == 1:
        return _job_arrival(instance_data)
    elif scenario_id == 2:
        return _machine_breakdown(instance_data)
    elif scenario_id == 3:
        return _processing_variation(instance_data)
    elif scenario_id == 4:
        return _combined_events(instance_data)
    return instance_data  # static/default

def _job_arrival(data):
    modified = copy.deepcopy(data)
    # Example: add a simple new job at t=20
    new_job = [(0, 3), (2, 5), (1, 4)]
    modified['jobs'].append(new_job)
    modified['num_jobs'] = len(modified['jobs'])
    modified['arrival_time'] = 20
    return modified

def _machine_breakdown(data):
    modified = copy.deepcopy(data)
    modified['breakdowns'] = [
        {'machine': 2, 'start': 15, 'duration': 5},
        {'machine': 4, 'start': 35, 'duration': 10},
    ]
    return modified

def _processing_variation(data):
    modified = copy.deepcopy(data)
    noise_std = 0.05  # 5% processing time noise
    for job in modified['jobs']:
        for i, (machine, time) in enumerate(job):
            noisy_time = max(1, int(np.random.normal(loc=time, scale=noise_std * time)))
            job[i] = (machine, noisy_time)
    return modified

def _combined_events(data):
    d = _job_arrival(data)
    d = _machine_breakdown(d)
    d = _processing_variation(d)
    return d
