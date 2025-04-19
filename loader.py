# ga_simulation_framework/loader.py

def load_instances(path):
    instances = {}
    with open(path, 'r') as file:
        lines = file.readlines()

    current_instance = None
    current_data = []
    reading = False

    for line in lines:
        line = line.strip()
        if line.startswith("instance"):
            if current_instance and current_data:
                instances[current_instance] = parse_instance(current_data)
                current_data = []
            current_instance = line.replace("instance", "").strip()

        elif line.startswith("+"):
            reading = not reading  # toggle reading block
        elif reading and line:
            current_data.append(line)

    if current_instance and current_data:
        instances[current_instance] = parse_instance(current_data)

    return instances


def parse_instance(lines):
    header = lines[0].split()
    num_jobs, num_machines = int(header[0]), int(header[1])
    job_data = []

    for line in lines[1:]:
        tokens = list(map(int, line.strip().split()))
        operations = [(tokens[i], tokens[i+1]) for i in range(0, len(tokens), 2)]
        job_data.append(operations)

    return {
        "num_jobs": num_jobs,
        "num_machines": num_machines,
        "jobs": job_data
    }