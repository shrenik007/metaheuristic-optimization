

"""
Author:
file:
Rename this file to TSP_x.py where x is your student number 
"""
import json
import multiprocessing
import os
import random
import sys
from datetime import datetime

from Individual import *
from Individual import Individual

from utils import get_normalised_fitness

myStudentNum = '183334'  # Replace 12345 with your student number
random.seed(myStudentNum)


class BasicTSP:

    def __init__(self, _fName, _popSize, _mutationRate, _maxIterations, _kwargs):
        """
        Parameters and general variables
        """

        self.population = []
        self.matingPool = []
        self.best = None
        self.popSize = _popSize
        self.genSize = None
        self.mutationRate = _mutationRate
        self.maxIterations = _maxIterations
        self.iteration = 0
        self.fName = _fName
        self.data = {}

        self.list_of_fitness = []
        self.new_population = []
        self.loop_best_iteration = 0
        self.new_mating_pool = []
        self.kwargs = _kwargs
        self.pop_generation_choice = self.kwargs['pop_generation_choice']
        self.crossover_choice = self.kwargs['crossover_choice']
        self.selection_choice = self.kwargs['selection_choice']
        self.mutation_choice = self.kwargs['mutation_choice']

        self.readInstance()
        self.initPopulation()

    def get_chromosome_bw_mark(self, next_mark, list_of_fitness):
        new_element = next(
            filter(lambda item: item['starting_point'] <= next_mark < item['ending_point'], list_of_fitness))
        return new_element['chromosomes']

    def readInstance(self):
        """
        Reading an instance from fName
        """
        file = open(self.fName, 'r')
        self.genSize = int(file.readline())
        self.data = {}
        for line in file:
            (id, x, y) = line.split()
            self.data[int(id)] = (int(x), int(y))
        file.close()

    def initPopulation(self):
        """
        Creating random individuals in the population
        """
        for i in range(0, self.popSize):
            individual = Individual(self.genSize, self.data, self.pop_generation_choice)
            individual.computeFitness()
            self.population.append(individual)

        self.best = self.population[0].copy()
        starting_point = 0
        for ind_i in self.population:
            # the below function will transform the fitness of a chomosone to normalised value as while deciding
            # better fitness we keep in mind that lesser the euclidean distance better is the fitness
            population_fitness = ind_i.getFitness()
            ending_point = starting_point + population_fitness
            self.list_of_fitness.append({
                'chromosomes': ind_i,
                'starting_point': starting_point,
                'ending_point': ending_point,
                'population_fitness': population_fitness
            })
            starting_point += population_fitness
            if self.best.getFitness() > ind_i.getFitness():
                self.best = ind_i.copy()
        # print("Best initial sol: ", self.best.getFitness())

    def updateBest(self, candidate):
        if self.best == None or candidate.getFitness() < self.best.getFitness():
            self.best = candidate.copy()
            self.loop_best_iteration = self.iteration
            # print("iteration: ", self.iteration, "best: ", self.best.getFitness())

    def randomSelection(self):
        """
        Random (uniform) selection of two individuals
        """
        indA = self.matingPool[random.randint(0, self.popSize-1)]
        indB = self.matingPool[random.randint(0, self.popSize-1)]
        return [indA, indB]

    def stochasticUniversalSampling(self):
        """
        The stochastic universal sampling is a method of selecting best fit parents from the population.
        After selecting best parents we fill the new mating pool
        After new mating pool is ready we randomly select 2 parents from that mating pool keeping in mind
        that 2 randomly selected elements are not same.
        """
        NUMBER_OF_PARENTS = round(self.popSize)
        sum_fitness = self.list_of_fitness[-1]['ending_point']
        # print(sum_fitness)

        point_distance = sum_fitness / NUMBER_OF_PARENTS
        start_point = random.uniform(0, point_distance)

        # ruler_marking = []
        next_mark = start_point
        #  the below loop will create new mating pool based on stochastic universal sampling
        # if not self.new_mating_pool:
        for x in range(NUMBER_OF_PARENTS):
            # ruler_marking.append(next_mark)
            self.new_mating_pool.append(self.get_chromosome_bw_mark(next_mark, self.list_of_fitness))
            next_mark += point_distance
        indA = indB = None
        #  the below while loop takes care whether the 2 randomly selected parent are not similar
        while indA == indB:
            indA = self.new_mating_pool[random.randint(0, NUMBER_OF_PARENTS - 1)]
            indB = self.new_mating_pool[random.randint(0, NUMBER_OF_PARENTS - 1)]
        # print(indA, indB)
        return [indA, indB]

    def uniformCrossover(self, indA, indB):
        """
        Your Uniform Crossover Implementation
        """
        random_points = random.sample(range(0, len(indA.genes) - 1), round(len(indA.genes) / 2))

        new_child1 = [None] * self.genSize
        new_child2 = [None] * self.genSize

        for index in random_points:
            new_child1[index] = indA.genes[index]
            new_child2[index] = indB.genes[index]

            # for new_index in range(len(indA.genes)):
            #     if not new_child1[new_index]:
        for internal_B in indB.genes:
            if internal_B not in new_child1:
                if None in new_child1:
                    new_index = new_child1.index(None)
                    # print(new_index, 'new')
                    new_child1[new_index] = internal_B
                    # break
            # if not new_child2[new_index]:
            #     for internal_A in indA.genes:
            #         if internal_A not in new_child2:
            #             new_child2[new_index] = internal_A
            #             break
        indA.genes = new_child1
        # indB.genes = new_child2
        return indA, indB

    def pmxCrossover(self, indA, indB):
        """
        Your PMX Crossover Implementation
        new_child1 and new_child2 are 2 children whcih are result of PMX crossover
        sub_list1 and sub_list2 are 2 randomly selected range of genes from 2 respective parents
        """
        index1 = random.randint(0, self.genSize - 1)
        index2 = random.randint(0, self.genSize - 1)

        if index1 < index2:
            min_index = index1
            max_index = index2
        else:
            min_index = index2
            max_index = index1
        sub_list_1 = indA.genes[min_index:max_index]
        sub_list_2 = indB.genes[min_index:max_index]
        #  filling all genes of new child as None
        new_child1 = [None] * self.genSize
        new_child2 = [None] * self.genSize

        #  replace part of randomly selected sublist of parents in the new child
        new_child1[min_index:max_index] = sub_list_2
        new_child2[min_index:max_index] = sub_list_1

        for index in range(len(indA.genes)):
            #  below if condition is used to select only suc elements which are not swapped from parent
            if not new_child1[index]:
                if indA.genes[index] not in new_child1:
                    new_child1[index] = indA.genes[index]
                else:
                    #  here the loop will take place recursively
                    #  until and unless it will an element which is not present in the new_child1
                    new_index = sub_list_2.index(indA.genes[index])
                    temp_ele = sub_list_1[new_index]
                    while temp_ele in new_child1:
                        #  this loop will break when it finds an element which is not present in the new child
                        new_index = sub_list_2.index(temp_ele)
                        temp_ele = sub_list_1[new_index]
                    new_child1[index] = temp_ele

            # if not new_child2[index]:
            #     if indB.genes[index] not in new_child2:
            #         new_child2[index] = indB.genes[index]
            #     else:
            #         #  here the loop will take place recursively
            #         #  until and unless it will an element which is not present in the new_child2
            #         new_index = sub_list_1.index(indB.genes[index])
            #         temp_ele = sub_list_2[new_index]
            #         while temp_ele in new_child2:
            #             #  this loop will break when it finds an element which is not present in the new child
            #             new_index = sub_list_1.index(temp_ele)
            #             temp_ele = sub_list_2[new_index]
            #         new_child2[index] = temp_ele
        indA.genes = new_child1
        # indB.genes = new_child2
        return indA, indB

    def reciprocalExchangeMutation(self, ind):
        """
        Your Reciprocal Exchange Mutation implementation
        """
        if random.random() > self.mutationRate:
            return
        indexA = random.randint(0, self.genSize - 1)
        indexB = random.randint(0, self.genSize - 1)

        tmp = ind.genes[indexA]
        ind.genes[indexA] = ind.genes[indexB]
        ind.genes[indexB] = tmp

        ind.computeFitness()
        self.updateBest(ind)
        return ind

    def inversionMutation(self, ind):
        """
        Your Inversion Mutation implementation
        """
        if random.random() > self.mutationRate:
            return
        indexA = random.randint(0, self.genSize-1)
        indexB = random.randint(0, self.genSize-1)

        if indexA < indexB:
            min_index = indexA
            max_index = indexB
        else:
            min_index = indexB
            max_index = indexA

        sub_list = ind.genes[min_index:max_index]
        sub_list.reverse()
        ind.genes[min_index:max_index] = sub_list
        ind.computeFitness()
        self.updateBest(ind)
        return ind

    def crossover(self, indA, indB):
        """
        Executes a 1 order crossover and returns a new individual
        """
        child = []
        tmp = {}

        indexA = random.randint(0, self.genSize-1)
        indexB = random.randint(0, self.genSize-1)

        for i in range(0, self.genSize):
            if i >= min(indexA, indexB) and i <= max(indexA, indexB):
                tmp[indA.genes[i]] = False
            else:
                tmp[indA.genes[i]] = True
        aux = []
        for i in range(0, self.genSize):
            if not tmp[indB.genes[i]]:
                child.append(indB.genes[i])
            else:
                aux.append(indB.genes[i])
        child += aux
        return child

    def mutation(self, ind):
        """
        Mutate an individual by swaping two cities with certain probability (i.e., mutation rate)
        """
        if random.random() > self.mutationRate:
            return
        indexA = random.randint(0, self.genSize-1)
        indexB = random.randint(0, self.genSize-1)

        tmp = ind.genes[indexA]
        ind.genes[indexA] = ind.genes[indexB]
        ind.genes[indexB] = tmp

        ind.computeFitness()
        self.updateBest(ind)

    def updateMatingPool(self):
        """
        Updating the mating pool before creating a new generation
        """
        self.matingPool = []
        for ind_i in self.population:
            self.matingPool.append(ind_i.copy())

    def newGeneration(self):
        """
        Creating a new generation
        1. Selection
        2. Crossover
        3. Mutation
        """
        s_end_time = datetime.now()
        for i in range(0, len(self.population)):
            """
            Depending of your experiment you need to use the most suitable algorithms for:
            1. Select two candidates
            2. Apply Crossover
            3. Apply Mutation
            """
            if self.selection_choice == 0:
                canA, canB = self.randomSelection()
            else:
                start_time = datetime.now()
                canA, canB = self.stochasticUniversalSampling()
                end_time = datetime.now() - start_time
                s_end_time += end_time
                # print('Endtime of new stochashtic mating pool', end_time)
            # cross_over_new_child = self.crossover(canA, canB)

            #  based on the crossover choice we select type of crossover to be selected
            #  PMX crossover is performed when self.crossover_choice == 1
            #  Uniform crossover is performed when self.crossover_choice == 2
            # print('Population Generated---------------')
            if self.crossover_choice == 1:
                cross_over_new_child1, cross_over_new_child2 = self.pmxCrossover(canA, canB)
            else:
                cross_over_new_child1, cross_over_new_child2 = self.uniformCrossover(canA, canB)
            # print('Crossover done----------------')
            # self.mutation(canA)
            #  based on the mutation choice we select type of mutation to be selected
            #  reciprocal exchange mutation is performed when self.mutation_choice == 1
            #  inversion mutation is performed when self.mutation_choice == 2
            if self.mutation_choice == 1:
                new_pop1 = self.reciprocalExchangeMutation(cross_over_new_child1)
                # new_pop2 = self.reciprocalExchangeMutation(cross_over_new_child2)
            else:
                new_pop1 = self.inversionMutation(cross_over_new_child1)
                # new_pop2 = self.inversionMutation(cross_over_new_child2)
            #  sometimes new_pop1 or new_pop2 comes None because random.random() > self.mutationRate
            if new_pop1:
                self.population[i] = new_pop1
                # new_population.append(new_pop1)
            # if new_pop2:
            #     new_population.append(new_pop2)

    def GAStep(self):
        """
        One step in the GA main algorithm
        1. Updating mating pool with current population
        2. Creating a new Generation
        """

        self.updateMatingPool()
        self.newGeneration()

    def search(self):
        """
        General search template.
        Iterates for a given number of steps
        """
        self.iteration = 0
        start_time = datetime.now()
        # print('Loop started at', start_time)
        while self.iteration < self.maxIterations:
            # print(self.iteration)
            self.GAStep()
            self.iteration += 1
        end_time = datetime.now()
        print("Iteration: ", self.loop_best_iteration, " Fitness Values:", self.best.getFitness())
        # print('Total time taken to complete internal iterations:', end_time - start_time)


if len(sys.argv) < 2:
    print("Error - Incorrect input")
    print("Expecting python BasicTSP.py [instance] ")
    sys.exit(0)


problem_file = sys.argv[1]

json_file = open('configs.json', 'r')
configs = json.loads(json_file.read())


def run_single_config(configs):
    start1 = datetime.now()
    iteration_sum_fitness = 0
    pop_size = configs['pop_size']
    mutation_rate = configs['mutation_rate']
    max_iterations = configs['max_iterations']

    kwargs = configs['kwargs']

    f = open(os.path.join(problem_file.split(".")[0], configs['output_file_name'] + '.txt'), 'w')
    f.write(f'**********************CONFIG NUMBER {configs["config"]}****************************************\n')
    for i in range(5):
        print(f'main iteration {i} \n')
        f.write(f'Main iteration {i} started\n')
        start = datetime.now()
        ga = BasicTSP(sys.argv[1], pop_size, mutation_rate, max_iterations, kwargs)
        ga.search()
        fitness = ga.best.getOriginalFitness()
        iteration_sum_fitness += fitness
        end = datetime.now()
        f.write(f'Time taken to for current iteration {end - start} and best fitness is {fitness}\n')
    f.write('**************************************************************\n')
    average_fitness = iteration_sum_fitness / 5
    end1 = datetime.now()
    f.write(f'Population size={pop_size}, mutation rate= {mutation_rate}, max iterations={max_iterations}\n')
    f.write(f'Average fitness={average_fitness}\n')
    f.write(f'Total time taken to run all iterations {end1 - start1}\n')
    f.close()

#  Distributed programming
try:
    os.mkdir(problem_file.split(".")[0])
except OSError:
    print("Creation of the directory %s failed" % problem_file)
# pool = multiprocessing.Pool()
# pool.map(run_single_config, configs[0:1])

# sequencial programming
for config in configs:
    run_single_config(config)

