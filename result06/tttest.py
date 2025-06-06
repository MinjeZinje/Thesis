from loader import load_instances
from rescheduler import simulate_ts_with_rescheduling

# Load first instance (e.g. ft06)
instances = load_instances("data.txt")
inst = instances[0]  # or use for-loop for all instances

scenario_names = ["Static", "NewJob", "Breakdown", "TimeNoise", "Mixed"]

for sid, name in enumerate(scenario_names):
    mk = []
    for _ in range(5):  # Run 5 times for SD
        history = simulate_ts_with_rescheduling(inst, sid)
        makespan = history[-1][1]
        mk.append(makespan)
    sd = (max(mk) - min(mk)) / 2 if len(mk) > 1 else 0.0
    print(f"{name}: {mk}  SD={sd:.2f}")
