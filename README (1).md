# Hybrid Genetic Algorithms for Dynamic Job Shop Scheduling (DJSSP)

This repository contains the code and experiments for the master’s thesis:

**Hybrid Genetic Algorithms in Dynamic Job Shop Scheduling Problems**  
Minjin Gantulga — Otto‑von‑Guericke University Magdeburg, 2025

The project benchmarks several Hybrid Genetic Algorithm (HGA) variants and a Tabu Search (TS) baseline under *event‑driven* dynamic scenarios (new job arrivals, machine breakdowns, processing‑time noise, and mixed events). Experiments are run on standard FT and LA instances with repeated simulations for robust statistics.

---

## Highlights
- **Event‑driven rescheduling**: rebuilds the sub‑problem at every disruption and re‑optimizes only the unfinished portion.
- **Eight algorithmic baselines** out‑of‑the‑box: `GA`, `GAKK`, `GASPT`, `GALPT`, `GASRPT`, `GALRPT`, `GAMIX`, `TS`.
- **Reproducible scenarios**: scripted event streams so all algorithms see the *same* sequence of disruptions.
- **Statistical analysis**: Friedman / Nemenyi / Wilcoxon utilities and plotting scripts.

---

## Repository Layout
```
.
├── data/                 # FT*, LA* benchmark instances (place here)
├── results/              # CSV logs, summaries, and figures will be written here
├── src/
│   ├── main.py           # Experiment runner: loops instances × scenarios × algorithms
│   ├── loader.py         # Loads FT/LA instances
│   ├── scenario.py       # Injects dynamic events (arrivals, breakdowns, time noise)
│   ├── rescheduler.py    # Freezes finished ops, builds reduced sub‑problem
│   ├── ga.py             # GA core: selection, PBX crossover, swap mutation, elitism
│   ├── heuristics.py     # KK, SPT, LPT, SRPT, LRPT seeds and mixers (GAMIX)
│   ├── tabu.py           # Tabu Search baseline (tenure, aspiration)
│   ├── scheduler.py      # Decoding, simulation, makespan/stability metrics
│   └── utils/            # Helpers (caching, multiprocessing, RNG, plotting)
├── analysis/
│   ├── summary_tools.py  # Aggregation helpers
│   ├── gamix_test.py     # Friedman + Wilcoxon demo on summary.csv
│   └── crit.py           # Critical‑difference plot example
├── requirements.txt
└── README.md
```

> **Note**: Filenames above reflect the thesis text. If your repository uses different paths, adjust the commands below accordingly.

---

## Quick Start

### 1) Environment
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Prepare Data
Download standard **FT** and **LA** JSSP instances and place them under `data/`.  
Example: `data/FT06.txt`, `data/FT10.txt`, `data/LA30.txt`.

### 3) Run an Experiment
Run a single combination (example shown):
```bash
python -m src.main \
  --instance FT10 \
  --scenario new_job \
  --algorithm GAMIX \
  --replications 20 \
  --time_budget 5.0 \
  --seed 42 \
  --out_dir results/FT10_new_job_GAMIX
```
Common flags (adapt if your CLI differs):
- `--instance` one of `FT06, FT10, FT20, LA01 … LA40`
- `--scenario` one of `static, new_job, breakdown, time_noise, mixed`
- `--algorithm` one of `GA, GAKK, GASPT, GALPT, GASRPT, GALRPT, GAMIX, TS`
- `--replications` number of independent runs
- `--time_budget` seconds per rescheduling call (event‑driven)
- `--seed` RNG seed for reproducibility
- `--out_dir` where CSV logs and figures are saved

Outputs include per‑run logs and a `summary.csv` with columns like:
```
Instance,Scenario,Algorithm,Replication,Makespan,Stability,Runtime,Seed
```

### 4) Batch All Experiments
The driver in `src/main.py` can sweep all (instance × scenario × algorithm) combinations, with multiprocessing for speed. Adjust the configuration block or pass a config file (YAML/JSON) if supported by your codebase.

---

## Scenarios (Event‑Driven)

- **static**: baseline (no disruptions).  
- **new_job**: scripted job insertions (e.g., at `t={20,40,60}` with 3–5 ops/job).  
- **breakdown**: machine downtimes (e.g., `M2@t=15:Δ5`, `M4@t=35:Δ10`).  
- **time_noise**: ±10% truncated‑normal perturbation of operation times.  
- **mixed**: combinations of the above.

All scenarios use the *same* scripted stream per run so comparisons are fair.

---

## Algorithms

- **GA**: random initialization (baseline).  
- **GAKK**: KK‑seeded initialization (25% seeded by default).  
- **GASPT/GALPT/GASRPT/GALRPT**: SPT/LPT/SRPT/LRPT seeding, respectively.  
- **GAMIX**: mixed seeds (KK + SPT + LPT + SRPT + LRPT).  
- **TS**: Tabu Search baseline with tenure + aspiration; same decoder/simulator as GA.

> The GA uses job‑based permutation encoding, PBX crossover, swap mutation, elitism, and optional local search on elites. Finished operations are frozen at each event; only the remaining sub‑problem is re‑optimized.

---

## Reproducing Figures & Stats

After collecting `summary.csv` files, you can run the example analysis scripts:
```bash
# Friedman + pairwise Wilcoxon across (instance, scenario) blocks
python -m analysis.gamix_test  # expects analysis/summary.csv or set a path inside

# Critical‑difference diagram (edit avg ranks and CD inside)
python -m analysis.crit
```

You can also aggregate all result CSVs into a single `analysis/summary.csv` using your own notebook or `analysis/summary_tools.py` (if provided).

---

## Tips & Notes
- **Reproducibility**: fix global seeds, and—crucially—use the *same* scripted event stream across algorithms within a block.
- **Time budgets**: choose per‑event limits that reflect a realistic shop‑floor decision window.
- **Caching**: makespan caching and vectorized NumPy ops can significantly cut runtime.
- **Scale**: start with `FT06` to verify correctness; then ramp up to `FT10/FT20/LA*`.

---

## Citation
If you use this code or results, please cite the thesis:
```
Gantulga, M. (2025). Hybrid Genetic Algorithms in Dynamic Job Shop Scheduling Problems
(Master’s thesis). Otto‑von‑Guericke University Magdeburg.
```

---

## License
Choose a license for your repository (e.g., MIT, Apache‑2.0) and put it in `LICENSE`.
