"""
Author: Diarmuid Grimes, based on code of Alejandro Arbelaez
Insertion heuristics for quickly generating (non-optimal) solution to TSP
File contains two heuristics. 
First heuristic inserts the closest unrouted city to the previous city 
added to the route.
Second heuristic inserts randomly chosen unrouted city directly after its 
nearest city on the route
file: lab_tsp_insertion.py
"""

import math
import random
import sys
random.seed(12345)

def readInstance(fName):
    file = open(fName, 'r')
    size = int(file.readline())
    inst = {}
#    for line in file:
    for i in range(size):
        line=file.readline()
        (myid, x, y) = line.split()
        inst[int(myid)] = (int(x), int(y))
    file.close()
    return inst


def euclideanDistane(cityA, cityB):
    ##Euclidean distance
    #return math.sqrt( (cityA[0]-cityB[0])**2 + (cityA[1]-cityB[1])**2 )
    ##Rounding nearest integer
    return round( math.sqrt( (cityA[0]-cityB[0])**2 + (cityA[1]-cityB[1])**2 ) )


# Choose first city randomly, thereafter append nearest unrouted city to last city added to rpute
def insertion_heuristic1(instance):
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
#        print(bCity,bCost)
        for city_index in range(1, len(cities)):
            city = cities[city_index]
            cost = euclideanDistane(instance[current_city], instance[city])
#            print(cities[city_index], "Cost: ",cost)
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


# Choose unrouted city randomly, insert into route after nearest routed city 
def insertion_heuristic2(instance):
    cities = list(instance.keys())
    nCities=len(cities)
    cIndex = random.randint(0, len(instance)-1)

    tCost = 0

    solution = [cities[cIndex]]

    del cities[cIndex]

    while len(cities) > 0:
        cIndex = random.randint(0, len(cities)-1)
        nextCity = cities[cIndex]
        del cities[cIndex]
        bCost = euclideanDistane(instance[solution[0]], instance[nextCity])
        bIndex = 0
#        print(nextCity,bCost)
        for city_index in range(1, len(solution)):
            city = solution[city_index]
            cost = euclideanDistane(instance[nextCity], instance[city])
#            print(solution[city_index], "Cost: ",cost)
            if bCost > cost:
                bCost = cost
                bIndex = city_index
        solution.insert(bIndex+1, nextCity)
    for i in range(nCities):
        tCost+=euclideanDistane(instance[solution[i]], instance[solution[(i+1)%nCities]])

    return solution, tCost

def saveSolution(fName, solution, cost):
    file = open(fName, 'w')
    file.write(str(cost)+"\n")
    for city in solution:
        file.write(str(city)+"\n")
    file.close()

filename = sys.argv[1]
output = sys.argv[2]
#solution = insertion_heuristic1(readInstance(filename))
for i in range(len())
solution = insertion_heuristic1(readInstance(filename))
print ("===================")
print ("Input :", filename)
print ("Solution: ",solution)
saveSolution(output, solution[0], solution[1])





