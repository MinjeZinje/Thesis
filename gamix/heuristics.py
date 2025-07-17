import random

# === Base heuristics ===
def random_heuristic(data):
    seq = [j for j, ops in enumerate(data["jobs"]) for _ in ops]
    random.shuffle(seq)
    return seq

def kk_heuristic(data):
    jobs = sorted(range(len(data["jobs"])),
                  key=lambda j: data["jobs"][j][0][1])
    return [j for j in jobs for _ in data["jobs"][j]]

def spt_heuristic(data):
    jobs = sorted(range(len(data["jobs"])),
                  key=lambda j: sum(t for _, t in data["jobs"][j]))
    return [j for j in jobs for _ in data["jobs"][j]]

def lpt_heuristic(data):
    jobs = sorted(range(len(data["jobs"])),
                  key=lambda j: sum(t for _, t in data["jobs"][j]),
                  reverse=True)
    return [j for j in jobs for _ in data["jobs"][j]]

def srpt_heuristic(data):
    return spt_heuristic(data)

def lrpt_heuristic(data):
    return lpt_heuristic(data)

def mixed_heuristic(data):
    return random.choice([kk_heuristic, spt_heuristic,
                          lpt_heuristic, srpt_heuristic,
                          lrpt_heuristic])(data)

# === Core dictionary ===
HEURISTICS = {
    "GAKK":   kk_heuristic,
    "GASPT":  spt_heuristic,
    "GALPT":  lpt_heuristic,
    "GASRPT": srpt_heuristic,
    "GALRPT": lrpt_heuristic,
    "GAMIX":  mixed_heuristic,
    "GA":     random_heuristic,
}

# === GAMIX ablations ===
BASE = [kk_heuristic, spt_heuristic, lpt_heuristic, srpt_heuristic, lrpt_heuristic]

class MixedHeuristic:
    def __init__(self, keep, label):
        self.keep = keep
        self.__name__ = label  # ensures compatibility with multiprocessing
    def __call__(self, data):
        return random.choice(self.keep)(data)

def make_mix(exclude, label):
    keep = [h for h in BASE if h.__name__ not in exclude]
    return MixedHeuristic(keep, label)

ABLATIONS = {
    "GAMIX_no_GALPT":    make_mix({"lpt_heuristic"}, "GAMIX_no_GALPT"),
    "GAMIX_no_GASRPT":   make_mix({"srpt_heuristic"}, "GAMIX_no_GASRPT"),
    "GAMIX_no_GAKK":     make_mix({"kk_heuristic"}, "GAMIX_no_GAKK"),
    "GAMIX_no_GASPT":    make_mix({"spt_heuristic"}, "GAMIX_no_GASPT"),
    "GAMIX_no_GALRPT":   make_mix({"lrpt_heuristic"}, "GAMIX_no_GALRPT"),
    "GAMIX_no_LPT_SRPT": make_mix({"lpt_heuristic", "srpt_heuristic"}, "GAMIX_no_LPT_SRPT"),
}

HEURISTICS.update(ABLATIONS)
