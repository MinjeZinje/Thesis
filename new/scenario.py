import copy

def apply_scenario(instance_data, scenario_id):
    modified = copy.deepcopy(instance_data)

    if scenario_id == 1:
        modified['arrival_time'] = 20

    elif scenario_id == 2:
        modified['breakdowns'] = [
            {'machine': 2, 'start': 15, 'duration': 5},
            {'machine': 4, 'start': 35, 'duration': 10},
        ]

    elif scenario_id == 3:
        modified['processing_noise'] = True  # interpreted by rescheduler if needed

    elif scenario_id == 4:
        modified['arrival_time'] = 20
        modified['breakdowns'] = [
            {'machine': 2, 'start': 15, 'duration': 5},
            {'machine': 4, 'start': 35, 'duration': 10},
        ]
        modified['processing_noise'] = True

    return modified
