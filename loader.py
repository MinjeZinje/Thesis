# loader.py

def load_instances(path):
    instances = []
    with open(path, 'r') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or '+' in line:
            i += 1
            continue

        if "instance" in line.lower():
            name = line.strip().split()[1]
            i += 1
            continue

        # Parse size
        if line and line[0].isdigit():
            parts = line.split()
            num_jobs, num_machines = int(parts[0]), int(parts[1])
            i += 1
            jobs = []

            for _ in range(num_jobs):
                op_parts = list(map(int, lines[i].strip().split()))
                job = [(op_parts[j], op_parts[j+1]) for j in range(0, len(op_parts), 2)]
                jobs.append(job)
                i += 1

            instances.append({
                "name": name,
                "num_jobs": num_jobs,
                "num_machines": num_machines,
                "jobs": jobs
            })
        else:
            i += 1

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
