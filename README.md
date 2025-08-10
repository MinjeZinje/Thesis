Hybrid Genetic Algorithms for Dynamic Job Shop Scheduling (DJSSP)
This repository contains the code used in the thesis “Hybrid genetic algorithms in dynamic job shop scheduling problems.”
It benchmarks several Hybrid Genetic Algorithm (HGA) variants and a Tabu Search (TS) baseline under event-driven dynamic scenarios (new job arrivals, machine breakdowns, processing-time noise, and a mixed case) on standard FT / LA instances.

Key features
Event-driven rescheduling: react immediately to disruptions; freeze completed/in-process ops; rebuild the remaining subproblem.

Multiple algorithm variants: GA with KK/SPT/LPT/SRPT/LRPT seeds, a mixed (GAMIX) population, pure GA, and TS baseline.

Reproducible experiments: consistent scenario streams across algorithms; multi-rep simulation with summary CSVs.

Plotting & stats: boxplots, summary tables, and critical-difference style rank visuals; scripts for Friedman/Wilcoxon.

Repository layout
.
├── main.py                # Experiment runner: loops instances × scenarios × algorithms
├── ga.py                  # Genetic algorithm core (selection, PBX crossover, mutation, elitism)
├── heuristics.py          # KK / SPT / LPT / SRPT / LRPT seeding + mixed (GAMIX) helpers
├── scheduler.py           # Decoder + simulator (makespan evaluation; precedence & capacity)
├── rescheduler.py         # Event-driven rescheduling logic
├── scenario.py            # Scenario definitions (arrivals, breakdowns, time-noise, mixed)
├── tabu.py                # Tabu Search baseline
├── loader.py              # (If present) Instance loader for FT / LA data
│
├── result/                # Run outputs (per-run CSVs, aggregate summary.csv)
├── boxplots/              # Plot scripts / generated figures
├── gamix/                 # GAMIX analyses, ablations, and helper scripts
├── illustrations/         # Architecture and workflow figures
├── tests/                 # Light tests / sanity checks
│
├── crit.py                # Example: critical difference / average rank visualization
├── gamix test.py          # Example: Friedman/Wilcoxon over summary.csv
└── requirements.txt       # (Add if not present) Python dependencies
Requirements
Python 3.10+ (recommended)

Packages: numpy, pandas, scipy, matplotlib
(Add anything else you import—e.g., tqdm, networkx, etc.)

Install:
python -m venv .venv
. .venv/bin/activate           # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
# If you don't have requirements.txt yet:
pip install numpy pandas scipy matplotlib
Data (FT / LA instances)
Place benchmark instance files under data/ (or the folder your loader expects).

Folder: data/FT/, data/LA/ (adjust if your loader.py uses a different path)

Format: standard FT/LA text format.

If files are already in the repo, you can skip this step. If not, include a short note in the README about where to obtain them.

Quick start
Most projects like this support running everything from main.py. If your CLI differs, tweak the flags below to match what argparse defines in main.py.

# Example: run all algorithms on FT06 & FT10 under all scenarios, 20 reps
python main.py \
  --instances FT06 FT10 \
  --scenarios static new_job time_noise breakdown mixed \
  --algos GA GAKK GASPT GALPT GASRPT GALRPT GAMIX TS \
  --reps 20 \
  --out result/

# Minimal smoke test (fast):
python main.py --instances FT06 --scenarios static --algos GA --reps 3 --out result/smoke
Outputs
Run CSVs will be written under result/. A typical aggregated file is result/summary.csv with columns like:

Instance,Scenario,Algorithm,Replicate,Seed,Makespan,[...]
Reproducing the thesis figures/tables
Aggregate results (if your runner doesn’t already create summary.csv, run your aggregator here or point to the correct file).

Boxplots:

# Example plot script (adjust to your filenames)
python boxplots/make_boxplots.py --in result/summary.csv --out boxplots/
Statistical tests:

# Friedman + pairwise Wilcoxon on pivoted summary
python "gamix test.py"   # expects result/summary.csv by default

Scenarios & algorithms (what’s implemented)
Scenarios: static, new_job (arrivals), time_noise (±10%), breakdown (machine downtime), mixed (all).

Algorithms:

GA (random init)

GAKK, GASPT, GALPT, GASRPT, GALRPT (seeded GA variants)

GAMIX (mixed seeding)

TS (tabu baseline; same decoder/simulator for fairness)

Default GA settings (as used in the experiments; change in code or via CLI if supported):

Population 200, Generations 1000, Crossover 0.95, Mutation 0.05, Elitism 0.10

Tournament selection k=3

Initial population: 25% heuristic-seeded, 75% random

Optional local search on elites (e.g., 30 swaps)

Reproducibility
The event stream is scripted so each algorithm sees the same disruptions.

Seeds: runs are repeated (e.g., 20x) with fixed seeds.
If your CLI exposes a seed, document it here (e.g., --seed 123). Otherwise, note where it’s set in code.

Performance tips
Enable multiprocessing for independent reps (already supported in code).

Use numpy-vectorized operators in GA loop (already implemented).

Caching: the scheduler caches makespans for repeated chromosomes (already implemented).

Troubleshooting
My plots are empty → Check that result/summary.csv has no missing columns; run a quick head to verify.

No such file: FT/LA instances → Confirm paths in loader.py and that your data/ folder contains the files.

CLI flags differ → Run python main.py --help and adjust the examples above.

Citation
If you use this code, please cite the thesis:

Minjin Gantulga (2025). Hybrid genetic algorithms in dynamic job shop scheduling problems. Otto-von-Guericke University Magdeburg.

(Replace with your final bib entry once available.)

License
[Choose a license] — e.g., MIT. (Add a LICENSE file if you haven’t yet.)

Contact
Questions or issues? Open a GitHub issue or email minjin.gantulga@st.ovgu.de.
