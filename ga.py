import random, numpy as np
from copy import deepcopy
from typing import List, Tuple

Op = Tuple[Tuple[int, int], Tuple[int, int]]          # ((job,op),(mach,dur))

class GeneticAlgorithm:
    def __init__(self, instance_data: dict,
                 pop_size=200, num_generations=1000,
                 crossover_rate=0.95, mutation_rate=0.05,
                 elitism_rate=0.10, local_search_swaps=30,
                 seed_ratio=0.25, rng_seed=None):
        self.data   = instance_data
        self.NP, self.G = pop_size, num_generations
        self.cx, self.mut = crossover_rate, mutation_rate
        self.elite, self.ls, self.seed = elitism_rate, local_search_swaps, seed_ratio
        self.rng = random.Random(rng_seed)

    # ---------- population ---------------------------------------------------
    def _rand_ind(self) -> List[int]:
        counts = [len(ops) for ops in self.data["jobs"]]
        seq = np.repeat(np.arange(len(counts)), counts)
        self.rng.shuffle(seq);  return seq.tolist()

    def _init_pop(self, heuristic):
        return [heuristic(self.data) if heuristic and self.rng.random() < self.seed
                else self._rand_ind() for _ in range(self.NP)]

    # ---------- decoding / fitness ------------------------------------------
    @staticmethod
    def _decode(ind: List[int], data: dict) -> List[Op]:
        p = [0] * data["num_jobs"]; out = []
        for j in ind:
            m, d = data["jobs"][j][p[j]]; out.append(((j, p[j]), (m, d))); p[j] += 1
        return out

    def _fit(self, ind, sched):  return sched.calculate_makespan(self._decode(ind, self.data))

    # ---------- GA operators -------------------------------------------------
    def _select(self, pop, fit):
        i, j = self.rng.randrange(self.NP), self.rng.randrange(self.NP)
        return pop[i] if fit[i] < fit[j] else pop[j]

    def _cx(self, p1, p2):
        """Order-based crossover that preserves duplicate job IDs."""
        size = len(p1)
        pos  = self.rng.sample(range(size), k=size // 2)
        c1, c2 = [None] * size, [None] * size

        # copy selected positions
        for i in pos:
            c1[i] = p1[i]
            c2[i] = p2[i]

        # required number of occurrences for each job
        job_cnt = {j: p1.count(j) for j in set(p1)}

        def _fill(child, parent):
            cnt = {j: 0 for j in job_cnt}
            for g in child:
                if g is not None:
                    cnt[g] += 1
            for i in range(size):
                if child[i] is None:
                    for g in parent:
                        if cnt[g] < job_cnt[g]:
                            child[i] = g
                            cnt[g] += 1
                            break

        _fill(c1, p2)
        _fill(c2, p1)
        return c1, c2


    def _mut(self, ind):
        i, j = self.rng.sample(range(len(ind)), 2); ind[i], ind[j] = ind[j], ind[i]; return ind

    def _ls(self, ind, sched):
        best, fbest = ind, self._fit(ind, sched)
        for _ in range(self.ls):
            cand = self._mut(ind.copy()); f = self._fit(cand, sched)
            if f < fbest: best, fbest = cand, f
        return best

    # ---------- main loop ----------------------------------------------------
    def run(self, instance_data, scheduler, heuristic_func=None):
        pop = self._init_pop(heuristic_func)
        for _ in range(self.G):
            fit = [self._fit(ind, scheduler) for ind in pop]
            elite_k = max(1, int(self.elite * self.NP))
            elite_idx = np.argsort(fit)[:elite_k]
            new_pop = [self._ls(deepcopy(pop[i]), scheduler) for i in elite_idx]
            while len(new_pop) < self.NP:
                p1, p2 = self._select(pop, fit), self._select(pop, fit)
                c1, c2 = (self._cx(p1, p2) if self.rng.random() < self.cx else (p1.copy(), p2.copy()))
                if self.rng.random() < self.mut: self._mut(c1)
                if self.rng.random() < self.mut: self._mut(c2)
                new_pop.extend([c1, c2])
            pop = new_pop[:self.NP]
        best = min(pop, key=lambda ind: self._fit(ind, scheduler))
        return best, self._fit(best, scheduler)
