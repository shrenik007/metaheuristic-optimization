import copy
import sys
import time
from utils import *
# random.seed(183334)


def main(lines, iterations=1, restarts=1, wp=0.4, tabu_tenure=5):
    """
    This is the main function for driving the GWSAT algorithm
    """
    variable_value = {}
    # this line get which variables involved in the clauses For eg: {'C1': [2, -3, 5] }
    clauses_dict,  list_of_variables = get_clause_dict(lines)
    # the below line of code gets clause and variable mappings and variable present in which clauses.
    # for eg variable_clause_dict has {'1': [C1, C3, C4]} and variable_clause_dict_full has {-10: {'C1': [-10, -16, 5]}}
    variable_clause_dict, variable_clause_dict_all = get_variable_clauses_mapping(clauses_dict)
    boolean_list = [True, False]
    # randomly assigning True or False to all the variables
    for variable in list_of_variables:
        random_number = random.randint(0, len(boolean_list) - 1)
        variable_value[abs(variable)] = boolean_list[random_number]
    # the main of maximum restarts
    for max_index in range(restarts):
        queue = []
        # the loop for max tries (iterations)
        for flip_index in range(iterations):
            # below line will fetch the list of clauses which are satisfied and which are not satisfied
            clauses_satisfied, clauses_not_satisfied = get_clauses_result(clauses_dict, variable_value)
            # check if length of satisfied clauses is equal to total number clauses
            if len(clauses_satisfied) == len(clauses_dict.keys()):
                print('Number of restarts', max_index)
                print('Number of flips in current restart', flip_index)
                return variable_value, max_index, flip_index
            random_unsat_index = random.randint(0, len(clauses_not_satisfied)-1)  # generate random number b/w 0 to 1
            # randomly select a clause from list of unsat clauses
            random_unsat_clause = clauses_not_satisfied[random_unsat_index]
            variable_value_copy = copy.deepcopy(variable_value)
            # the below code get the negative gain of all the variables in the randomly selected unsat clause
            negative_gain_dict, zero_list = get_variable_negative_gain(variable_value_copy,
                                                                       clauses_dict[random_unsat_clause],
                                                                       clauses_satisfied, clauses_dict,
                                                                       variable_clause_dict_all)
            # below code filters all the variables present in the tabu list.
            # only the variables which are not present in the tabu list are considered for the next steps
            final_dict = {k: v for k, v in negative_gain_dict.items() if k not in queue}
            if final_dict:
                if zero_list:
                    #  if any variable is having negative gain of 0 then we select them randomly if they are more than 1
                    random_zero = random.randint(0, len(zero_list) - 1)
                    value_to_flip = zero_list[random_zero]
                else:
                    # if none of them have negative gain of 0, then generate random number between 0 and 1
                    random_float = random.random()
                    if random_float < wp:
                        # choose randomwalk if random number less than wp
                        value_to_flip = select_variable_using_randomwalk([random_unsat_clause], clauses_dict)
                    else:
                        # select the variable having minimal negative gain
                        min_negative_gain = min(final_dict.items(), key=operator.itemgetter(1))[0]
                        value_to_flip = min_negative_gain
                # add the selected variable to flip to the tabu list
                if value_to_flip not in queue and -value_to_flip not in queue:
                    queue.append(value_to_flip)
                # if tabu list is full pop the first variable out
                if len(queue) > tabu_tenure:
                    queue.pop(0)
                # flip the variable which is selected
                variable_value[abs(value_to_flip)] = not variable_value[abs(value_to_flip)]
            else:
                #  do not flip any variable
                pass
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
    tabu_tenure = int(sys.argv[6])

    # reading the instance file
    f = open(instance, 'r')
    lines = f.readlines()

    runtime_per_execution = {}
    for index in range(max_executions):
        random.seed(183334+(index * 1000))  # generating random seed for each execution for more randomness
        print('------------------ Execution number', index, '--------------------')
        start_time = time.time()  # noting the start time
        # return valid solution (dictionary) or False as result
        result = main(lines, iterations, max_restarts, wp, tabu_tenure)
        # if dict is returned
        if result:
            elapsed_time = time.time() - start_time  # calculating the time required to run a particular execution
            runtime_per_execution[index] = {
                'runtime': elapsed_time,
                'restart_number': result[1],
                'iteration_number': result[2]
            }
            print(result)
            print('Time elapsed', elapsed_time)
            print('------------Solution found--------------')
        else:
            print('------------Solution not found--------------')
    print(runtime_per_execution)
    # below lines are storing various results into the file
    instance = instance.split("/")[1]
    instance = instance.split('.')[0].replace("-", "")
    main_end_time = time.time() - main_start_time
    f = open(f'results/walksat-{instance}-{max_executions}-{max_restarts}-{iterations}-{wp}-{tabu_tenure}.txt', 'w')
    f.write(f'\ninstance: {instance}')
    f.write(f'\nMax executions: {max_executions}')
    f.write(f'\nMax restarts: {max_restarts}')
    f.write(f'\nMax iterations (flips): {iterations}')
    f.write(f'\nwp: {wp}')
    f.write(f'\ntabu tenure: {tabu_tenure}')
    # f.write(f'\nruntime per execution: {runtime_per_execution}')
    f.write(f'\ntotal runtime: {main_end_time}')
    f.write(f"\nTotal valid solutions: {len(runtime_per_execution.keys())}")
    f.close()
    # plotting RTD graphs for different parameters like iteration number, CPU runtime
    plot_cummulative_empirical_rtd(runtime_per_execution, instance, 'walksat', 'runtime')
    plot_rtd_graph_on_iterations(runtime_per_execution, instance, 'walksat')
    # plot_cummulative_empirical_rtd(runtime_per_execution, instance, 'walksat', 'iteration_number')
