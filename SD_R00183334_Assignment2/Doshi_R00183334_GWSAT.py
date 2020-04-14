import copy
import os

from utils import *
import random
import sys
import time


def main(lines, iterations=1, restarts=1, wp=0.4):
    """
    This is the main function for driving the GWSAT algorithm
    """
    variable_value = {}
    # this line get which variables involved in the clauses For eg: {'C1': [2, -3, 5] }
    clauses_dict,  list_of_variables = get_clause_dict(lines)
    # the below line of code gets clause and variable mappings and variable present in which clauses.
    # for eg variable_clause_dict has {'1': [C1, C3, C4]} and variable_clause_dict_full has {-10: {'C1': [-10, -16, 5]}}
    variable_clause_dict, variable_clause_dict_full = get_variable_clauses_mapping(clauses_dict)
    boolean_list = [True, False]
    # randomly assigning True or False to all the variables
    for variable in list_of_variables:
        random_number = random.randint(0, len(boolean_list) - 1)
        variable_value[variable] = boolean_list[random_number]
    # the main of maximum restarts
    for max_index in range(restarts):
        # the loop for max tries (iterations)
        for flip_index in range(iterations):
            # below line will fetch the list of clauses which are satisfied and which are not satisfied
            clauses_satisfied, clauses_not_satisfied = get_clauses_result(clauses_dict, variable_value)
            # check if length of satisfied clauses is equal to total number clauses
            if len(clauses_satisfied) == len(clauses_dict.keys()):
                print('Number of restarts', max_index)
                print('Number of flips in current restart', flip_index)
                return variable_value, max_index, flip_index
            random_float = random.random()  # generating a random number between 0 and 1
            if random_float < wp:
                # if random number less than wp than select randomwalk to select the variable for flipping
                value_to_flip = select_variable_using_randomwalk(clauses_not_satisfied, clauses_dict)
            else:
                # if random number greater than wp call GSAT for variable selection for flipping
                variable_value_new = copy.deepcopy(variable_value)
                value_to_flip = select_variable_using_gsat_2(clauses_satisfied, clauses_not_satisfied,
                                                             variable_value_new,
                                                             variable_clause_dict_full)
            # flip the value of selected variable. From True to False or vice versa
            variable_value[abs(value_to_flip)] = not variable_value[abs(value_to_flip)]
    # return False if no valid solution is found.
    return False


if __name__ == '__main__':
    main_start_time = time.time()
    if len(sys.argv) < 5:
        print("Error - Incorrect input")
        sys.exit(0)
    # accepting parameters from command line
    instance = sys.argv[1]
    max_executions = int(sys.argv[2])
    max_restarts = int(sys.argv[3])
    iterations = int(sys.argv[4])
    wp = float(sys.argv[5])
    # reading the instance file
    f = open(instance, 'r')
    lines = f.readlines()
    runtime_per_execution = {}
    for index in range(max_executions):
        random.seed(183334 + (index * 1000))  # generating random seed for each execution for more randomness
        print('------------------ Execution number', index, '--------------------')
        start_time = time.time()  # noting the start time
        result = main(lines, iterations, max_restarts, wp)  # return valid solution (dictionary) or False as result
        # if dict is returned
        if result:
            elapsed_time = time.time() - start_time  # calculating the time required to run a particular execution
            runtime_per_execution[index] = {
                'runtime': elapsed_time,
                'restart_number': result[1],
                'iteration_number': result[2]
            }
            print('Execution number:', index)
            print(result)
            print('Time elapsed', elapsed_time)
            print('------------Solution found--------------')
        else:
            print('------------Solution not found--------------')

    # print(runtime_per_execution)
    # below lines are storing various results into the file
    instance = instance.split("/")[1]
    instance = instance.split('.')[0].replace("-", "")
    main_end_time = time.time() - main_start_time
    if not os.path.exists("results/rtd/gwsat"):
        os.makedirs("results/rtd/gwsat")
    if not os.path.exists("results/rtd/walksat"):
        os.makedirs("results/rtd/walksat")
    f = open(f'results/gwsat-{instance}-{max_executions}-{max_restarts}-{iterations}-{wp}.txt', 'w')
    f.write(f'\ninstance: {instance}')
    f.write(f'\nMax executions: {max_executions}')
    f.write(f'\nMax restarts: {max_restarts}')
    f.write(f'\nMax iterations (flips): {iterations}')
    f.write(f'\nwp: {wp}')
    # f.write(f'\nruntime per execution: {runtime_per_execution}')
    f.write(f'\ntotal runtime: {main_end_time}')
    f.write(f"\nTotal valid solutions: {len(runtime_per_execution.keys())}")
    f.close()

    # plotting RTD graphs for different parameters like iteration number, CPU runtime
    plot_cummulative_empirical_rtd(runtime_per_execution, instance, 'gwsat', 'runtime')
    plot_rtd_graph_on_iterations(runtime_per_execution, instance, 'gwsat')
    # plot_cummulative_empirical_rtd(runtime_per_execution, instance, 'gwsat', 'iteration_number')
