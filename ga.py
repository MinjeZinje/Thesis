import numpy as np
from copy import deepcopy
from functools import lru_cache


class GeneticAlgorithm:
    def __init__(
        self,
        instance_data,
        pop_size=60,
        num_generations=120,
        crossover_rate=0.95,
        mutation_rate=0.05,
        elitism_rate=0.10,
        local_search_swaps=15,
        seed_ratio=0.25,
        rng_seed=None,
    ):
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_rate = elitism_rate
        self.local_search_swaps = local_search_swaps
        self.seed_ratio = seed_ratio  # fraction of pop initialised by heuristic
        self.rng = np.random.default_rng(rng_seed)
        self._fitness_cache: dict[tuple, int] = {}

    #  Population helpers
    def _random_solution(self, instance_data):
        counts = [len(ops) for ops in instance_data["jobs"]]
        seq = np.repeat(np.arange(len(counts)), counts)
        self.rng.shuffle(seq)
        return seq.tolist()

    def _initialize_population(self, instance_data, heuristic_func):
        pop = []
        for _ in range(self.pop_size):
            if heuristic_func and self.rng.random() < self.seed_ratio:
                ind = heuristic_func(instance_data)
                ind = self._mutate(ind, 2)
            else:
                ind = self._random_solution(instance_data)
            pop.append(ind)
        return pop

    #  Decoding & fitness
    def _decode(self, individual, instance_data):
        op_idx = [0] * instance_data["num_jobs"]
        seq = []
        for jid in individual:
            mid, dur = instance_data["jobs"][jid][op_idx[jid]]
            seq.append(((jid, op_idx[jid]), (mid, dur)))
            op_idx[jid] += 1
        return seq

    def _evaluate(self, individual, scheduler, instance_data):
        key = tuple(individual)
        hit = self._fitness_cache.get(key)
        if hit is not None:
            return hit
        f = scheduler.calculate_makespan(self._decode(individual, instance_data))
        self._fitness_cache[key] = f
        return f

    #  GA operators
    def _selection(self, population, fitnesses):
        # tournament k=3
        idx = self.rng.integers(0, self.pop_size, 3)
        best = min(idx, key=lambda i: fitnesses[i])
        return population[best]

    def _crossover(self, p1, p2):
        size = len(p1)
        pos = self.rng.choice(size, size // 2, replace=False)
        c1, c2 = [None] * size, [None] * size
        for i in pos:
            c1[i], c2[i] = p1[i], p2[i]

        job_counts = {j: p1.count(j) for j in set(p1)}
        self._fill_fixed(c1, p2, job_counts)
        self._fill_fixed(c2, p1, job_counts)
        return c1, c2

    def _fill_fixed(self, child, parent, job_counts):
        cnt = {j: 0 for j in job_counts}
        for g in child:
            if g is not None:
                cnt[g] += 1
        for i in range(len(child)):
            if child[i] is None:
                for j in parent:
                    if cnt[j] < job_counts[j]:
                        child[i] = j
                        cnt[j] += 1
                        break

    def _mutate(self, individual, swaps=1):
        size = len(individual)
        for _ in range(swaps):
            i, j = self.rng.integers(0, size, 2)
            individual[i], individual[j] = individual[j], individual[i]
        return individual

    #  Optional local search (only on elites now)
    def _local_search(self, individual, scheduler, instance_data):
        best = individual
        best_f = self._evaluate(best, scheduler, instance_data)

        for _ in range(self.local_search_swaps):
            cand = best.copy()
            i, j = self.rng.integers(0, len(cand), 2)
            cand[i], cand[j] = cand[j], cand[i]
            f = self._evaluate(cand, scheduler, instance_data)
            if f < best_f:
                best, best_f = cand, f
        return best

    #  Main entry
    def run(self, instance_data, scheduler, heuristic_func=None):
        pop = self._initialize_population(instance_data, heuristic_func)

        for _ in range(self.num_generations):
            fit = [self._evaluate(ind, scheduler, instance_data) for ind in pop]

            # elites
            elite_n = int(self.elitism_rate * self.pop_size)
            elite_idx = np.argsort(fit)[:elite_n]
            new_pop = [self._local_search(deepcopy(pop[i]), scheduler, instance_data)
                       for i in elite_idx]

            # rest of population
            while len(new_pop) < self.pop_size:
                p1 = self._selection(pop, fit)
                p2 = self._selection(pop, fit)

                if self.rng.random() < self.crossover_rate:
                    c1, c2 = self._crossover(p1, p2)
                else:
                    c1, c2 = p1.copy(), p2.copy()

                if self.rng.random() < self.mutation_rate:
                    c1 = self._mutate(c1)
                if self.rng.random() < self.mutation_rate:
                    c2 = self._mutate(c2)

                new_pop.extend([c1, c2])

            pop = new_pop[: self.pop_size]

        # best individual
        final_f = [self._evaluate(ind, scheduler, instance_data) for ind in pop]
        best_idx = int(np.argmin(final_f))
        return pop[best_idx], final_f[best_idx]

