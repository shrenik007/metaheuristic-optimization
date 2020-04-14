"""
Author: Diarmuid Grimes, based on code of Alejandro Arbelaez
Insertion heuristics for quickly generating (non-optimal) solution to TSP
File contains two heuristics. 
First heuristic inserts the closest unrouted city to the previous city 
added to the route.
Second heuristic inserts randomly chosen unrouted city directly after its 
nearest city on the route
file: utils.py
"""

import math
import random
import sys
# random.seed(183334)


def get_normalised_fitness(current_fitness, normalisation_factor):
    """
    This is fitness transformation function. As we know the sum of euclidean distances is the fitness of each chromosome
    So the lesser the distance, the chromosome is fittest. In this case we normalise the distance where the
    highest distance will be converted to lower fitness value.
    Basically the normalisation_factor is used to reduce all the distances by that factor because when we divide the
    actual fitness by 1 the result is not too small e.g. 0.000000000000000123
    :param current_fitness: the sum euclidean distance of the chromosome
    :param normalisation_factor: number of genes in the chromosome
    :return: tranformed fitness
    """
    normalised_fitness = current_fitness / normalisation_factor
    return 1 / normalised_fitness


def euclideanDistane(cityA, cityB):
    """
        this function is written by Prof. Diarmuid Grimes
        this function return euclidean distance between 2 cities based on their latitude and longitude
    """
    return round(math.sqrt((cityA[0]-cityB[0])**2 + (cityA[1]-cityB[1])**2))


def insertion_heuristic1(instance):
    """
     this function is written by Prof. Diarmuid Grimes
     This function returns a TSP solution based on the Heuristic nearest neighbour method.
    """
    cities = list(instance.keys())
    cIndex = random.randint(0, len(instance)-1)

    tCost = 0

    solution = [cities[cIndex]]
    
    del cities[cIndex]

    current_city = solution[0]
    while len(cities) > 0:
        bCity = cities[0]
        bCost = euclideanDistane(instance[current_city], instance[bCity])
        bIndex = 0
        for city_index in range(1, len(cities)):
            city = cities[city_index]
            cost = euclideanDistane(instance[current_city], instance[city])
            if bCost > cost:
                bCost = cost
                bCity = city
                bIndex = city_index
        tCost += bCost
        current_city = bCity
        solution.append(current_city)
        del cities[bIndex]
    tCost += euclideanDistane(instance[current_city], instance[solution[0]])
    return solution, tCost





