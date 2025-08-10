import matplotlib.pyplot as plt
from loader import load_instances
from tabu import run_tabu_search
from scheduler import Scheduler

# 1. Load FT06 instance
instances = load_instances("data.txt")
ft06 = next(inst for inst in instances if inst['name'].lower() == 'ft06')

# 2. Run Tabu Search to get an optimal or near-optimal solution (makespan 55)
result = run_tabu_search(ft06, "ft06", "tmp.csv", 0, max_iters=300)
ops = result[0][4]  # The operation sequence: [((job_id, op_idx), (machine, duration)), ...]

# 3. Simulate and collect actual scheduling (start/finish times)
sched = Scheduler(ft06["num_machines"])
m_ready = [0] * ft06["num_machines"]
j_ready = {}
gantt = []

for (job_id, op_idx), (mach, dur) in ops:
    start = max(m_ready[mach], j_ready.get(job_id, 0))
    finish = start + dur
    gantt.append({
        "Job": f"J{job_id+1}",
        "Operation": op_idx + 1,
        "Machine": mach + 1,
        "Start": start,
        "Finish": finish
    })
    m_ready[mach] = finish
    j_ready[job_id] = finish

# 4. Plot Gantt chart (jobs as colors, machines as rows)
colors = ['#77b5fe', '#ffb347', '#90ee90', '#ff7f7f', '#b19cd9', '#c2b280']
fig, ax = plt.subplots(figsize=(15, 5))
for op in gantt:
    ax.barh(op["Machine"], op["Finish"] - op["Start"], left=op["Start"], color=colors[int(op["Job"][1])-1], edgecolor='black')
    duration = op["Finish"] - op["Start"]
    if duration > 1.5:  # Show label only if the bar is wide enough
        ax.text(op["Start"] + duration/2, op["Machine"], f'{op["Job"]}.{op["Operation"]}',
                va='center', ha='center', fontsize=12, fontweight='bold', color='white')


ax.set_yticks(range(1, ft06["num_machines"]+1))
ax.set_yticklabels([f"M{m}" for m in range(1, ft06["num_machines"]+1)])
ax.set_xlabel("Time")
ax.set_ylabel("Machine")
ax.set_title("FT06 - Optimal Schedule Gantt Chart")
plt.tight_layout()
plt.show()
