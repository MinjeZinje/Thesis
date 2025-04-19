import random
from copy import deepcopy

class GeneticAlgorithm:
    def __init__(self, pop_size, num_generations, crossover_rate, mutation_rate, elitism_rate):
        self.pop_size = pop_size
        self.num_generations = num_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_rate = elitism_rate

    def initialize_population(self, instance_data, heuristic_func=None):
        population = []
        for _ in range(self.pop_size):
            if heuristic_func and random.random() < 0.25:
                individual = heuristic_func(instance_data)
            else:
                individual = self.random_solution(instance_data)
            population.append(individual)
        return population

    def random_solution(self, instance_data):
        job_counts = [len(ops) for ops in instance_data['jobs']]
        job_sequence = []
        for job_id, count in enumerate(job_counts):
            job_sequence += [job_id] * count
        random.shuffle(job_sequence)
        return job_sequence

    def decode(self, individual, instance_data):
        job_op_indices = [0] * instance_data['num_jobs']
        operation_sequence = []
        for job_id in individual:
            op_idx = job_op_indices[job_id]
            machine, time = instance_data['jobs'][job_id][op_idx]
            operation_sequence.append(((job_id, op_idx), (machine, time)))
            job_op_indices[job_id] += 1
        return operation_sequence

    def evaluate_fitness(self, individual, scheduler, instance_data):
        decoded = self.decode(individual, instance_data)
        return scheduler.calculate_makespan(decoded)

    def selection(self, population, fitnesses):
        k = 3
        selected = random.choices(list(zip(population, fitnesses)), k=k)
        return min(selected, key=lambda x: x[1])[0]

    def crossover(self, parent1, parent2):
        size = len(parent1)
        pos = sorted(random.sample(range(size), size // 2))
        child1 = [None] * size
        child2 = [None] * size

        for i in pos:
            child1[i] = parent1[i]
            child2[i] = parent2[i]

        job_counts = {job_id: parent1.count(job_id) for job_id in set(parent1)}

        self.fill_fixed(child1, parent2, job_counts)
        self.fill_fixed(child2, parent1, job_counts)

        return child1, child2

    def fill_fixed(self, child, parent, job_counts):
        count = {job_id: 0 for job_id in job_counts}
        for gene in child:
            if gene is not None:
                count[gene] += 1

        for i in range(len(child)):
            if child[i] is None:
                for job_id in parent:
                    if count[job_id] < job_counts[job_id]:
                        child[i] = job_id
                        count[job_id] += 1
                        break

    def mutate(self, individual):
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
        return individual

    def run(self, instance_data, scheduler, heuristic_func=None):
        population = self.initialize_population(instance_data, heuristic_func)
        for gen in range(self.num_generations):
            fitnesses = [self.evaluate_fitness(ind, scheduler, instance_data) for ind in population]
            new_population = []

            elites = sorted(zip(population, fitnesses), key=lambda x: x[1])[:int(self.elitism_rate * self.pop_size)]
            new_population.extend([deepcopy(e[0]) for e in elites])

            while len(new_population) < self.pop_size:
                parent1 = self.selection(population, fitnesses)
                parent2 = self.selection(population, fitnesses)
                if random.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2)
                else:
                    child1, child2 = deepcopy(parent1), deepcopy(parent2)
                if random.random() < self.mutation_rate:
                    child1 = self.mutate(child1)
                if random.random() < self.mutation_rate:
                    child2 = self.mutate(child2)
                new_population.extend([child1, child2])

            population = new_population[:self.pop_size]

        fitnesses = [self.evaluate_fitness(ind, scheduler, instance_data) for ind in population]
        best_index = fitnesses.index(min(fitnesses))
        return population[best_index], fitnesses[best_index]
