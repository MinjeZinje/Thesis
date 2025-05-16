class Scheduler:
    def __init__(self, num_machines):
        self.num_machines = num_machines

    def calculate_makespan(self, chromosome):
        # chromosome: [((job_id, op_index), (machine, time)), ...]

        machine_available_time = [0] * self.num_machines
        job_end_time = {}  # Last finish time for each job

        for (job_id, op_idx), (machine, duration) in chromosome:
            # Start time = max of machine ready and job ready
            start_time = max(
                machine_available_time[machine],
                job_end_time.get(job_id, 0)
            )
            finish_time = start_time + duration

            # Update availability
            machine_available_time[machine] = finish_time
            job_end_time[job_id] = finish_time

        # Makespan is the latest time any machine finishes
        return max(machine_available_time)
