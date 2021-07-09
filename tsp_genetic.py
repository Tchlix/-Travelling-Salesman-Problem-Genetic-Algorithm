import numpy as np
import random
import operator
import pandas as pd


class TSPGenetic:

    def __init__(
            self,
            cities_distances: np.array,
            population:int,
            elite:int,
            mutation:float
    ):
        self.distances       = cities_distances
        self.cities_count    = cities_distances.shape[0]
        self.population_size = population
        self.elite_size      = elite
        self.mutation_rate   = mutation
        self.paths           = [[i for i in range(self.cities_count)] for _ in range(self.population_size)]
        self.best_path       = self.paths[0]
        self.best_distance   = self.__path_distance(self.best_path)

        self.__generate_first_population()

    def __generate_first_population(self):
        for i in range(self.population_size):
            random.shuffle(self.paths[i])

    def __path_distance(self, path):
        distance = 0
        for i in range(1, len(path)):
            distance += self.distances[path[i], path[i - 1]]
        distance += self.distances[path[len(path) - 1], path[0]]
        return distance

    # selecting parents

    def __rank_paths(self):
        fitness_results = {}
        for i, path in enumerate(self.paths):
            fitness_results[i] = 1 / self.__path_distance(path)
        return sorted(fitness_results.items(), key=operator.itemgetter(1), reverse=True)

    def __selection(self):
        selection_result = []
        population_result = self.__rank_paths()

        df = pd.DataFrame(np.array(population_result), columns=["Index", "Fitness"])
        df['cum_sum'] = df.Fitness.cumsum()
        df['cum_norm'] = df.cum_sum / df.Fitness.sum()

        for i in range(0, self.elite_size):
            selection_result.append(population_result[i][0])
        for i in range(self.population_size - self.elite_size):
            fit = random.random()
            for j in range(self.population_size):
                if fit <= df.iat[j, 3]:
                    selection_result.append(population_result[j][0])
                    break
        return selection_result

    def __extract_selection(self):
        return [self.paths[i] for i in self.__selection()]

    # breeding

    def __cross(self, path_parent_1, path_parent_2):
        path_child_1 = []
        start_parent_2 = int(random.random() * self.cities_count)
        end_parent_2 = int(random.random() * self.cities_count)
        if end_parent_2 < start_parent_2:
            start_parent_2, end_parent_2 = end_parent_2, start_parent_2
        for i in range(start_parent_2, end_parent_2):
            path_child_1.append(path_parent_1[i])
        path_child_2 = [city for city in path_parent_2 if city not in path_child_1]
        return path_child_1 + path_child_2

    def __cross_population(self, selected):
        children = []
        parents_count = self.population_size - self.elite_size
        parents = random.sample(selected, self.population_size)
        for i in range(self.elite_size):
            children.append(selected[i])
        for i in range(parents_count):
            children.append(self.__cross(parents[i], parents[len(selected) - i - 1]))
        return children

    # mutate some gens

    def __mutate(self, path):
        for i in range(self.cities_count):
            if random.random() < self.mutation_rate:
                j = int(random.random() * self.cities_count)
                path[i], path[j] = path[j], path[i]
        return path

    def __mutate_population(self, population):
        for i in range(self.population_size):
            population[i] = self.__mutate(population[i])
        return population

    # new generation

    def __new_generation(self):
        selected_paths = self.__extract_selection()
        children_paths = self.__cross_population(selected_paths)
        new_gene_paths = self.__mutate_population(children_paths)
        return new_gene_paths

    # genetic algorithm loop

    def update_solution(self):
        for i in range(0, self.population_size):
            distance = self.__path_distance(self.paths[i])
            if distance < self.best_distance:
                self.best_distance = distance
                self.best_path = self.paths[i].copy()
        return self.best_path, self.best_distance

    def solve_genetic(self):
        self.paths = self.__new_generation()
