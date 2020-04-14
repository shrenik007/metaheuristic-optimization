import operator
import random
import numpy as np
import matplotlib.pyplot as plt


def plot_cummulative_empirical_rtd(runtime_per_execution, instance_name, algo, attr='iteration_number'):
    """
    This function generated a matplotlib graph where on the y-axis there are values for P(solve) and on x-axis
    the values are iteration number or CPU run-time
    """
    plt.rcdefaults()
    k_successful_runs = len(runtime_per_execution.keys())
    required_list = [value[attr] for key, value in runtime_per_execution.items()]
    required_list.sort()
    new_dict = {required_list[item]: (item+1)/k_successful_runs for item in range(len(required_list))}
    plt.plot(list(new_dict.keys()), list(new_dict.values()))
    plt.ylabel('P(solve')
    plt.title(f'Cummulative empirical RTD of {algo.upper()} on {instance_name}')
    if attr == 'iteration_number':
        plt.xlabel("run-time [# iterations]")
        file_name = f"results/rtd/{algo}/iteration-RTD-{len(required_list)}-{instance_name}.png"
    else:
        plt.xlabel("run-time [CPU runtime]")
        file_name = f"results/rtd/{algo}/runtime-RTD-{len(required_list)}-{instance_name}.png"
    plt.savefig(file_name, bbox_inches="tight")
    plt.close()


def plot_rtd_graph_on_restarts(runtime_per_execution, instance_name, algo):
    """
    This will plot a bar graph for number of restarts on x-axis and cpu-time on y-axis
    """
    restarts_list = [value['restart_number'] for key, value in runtime_per_execution.items()]
    runtime_list = [value['runtime'] for key, value in runtime_per_execution.items()]
    plt.xticks(restarts_list)
    plt.bar(restarts_list, runtime_list, align='center', alpha=0.5)
    plt.xlabel("number of restarts")
    plt.ylabel('cpu time (seconds)')
    plt.title(f'Runtime distribution for {instance_name} (restarts)')
    plt.savefig(f"results/rtd/{algo}/RTD-restarts-{len(runtime_list)}-{instance_name}.png", bbox_inches="tight")
    plt.close()


def plot_rtd_graph_on_iterations(runtime_per_execution, instance_name, algo):
    """
        This will plot a bar graph for number of iterations on x-axis and cpu-time on y-axis
    """
    plt.rcdefaults()
    iterations_list = [value['iteration_number'] for key, value in runtime_per_execution.items()]
    runtime_list = [value['runtime'] for key, value in runtime_per_execution.items()]
    max_val = max(iterations_list)
    plt.xticks(np.arange(0, max_val, step=100))
    plt.xlabel("number of iterations")
    plt.ylabel('cpu time (seconds)')
    plt.bar(iterations_list, runtime_list, align='center', alpha=0.5)
    plt.title(f'Runtime distribution for {instance_name} (iterations)')
    plt.savefig(f"results/rtd/{algo}/RTD-iterations-{len(runtime_list)}-{instance_name}.png", bbox_inches="tight")
    plt.close()


def get_variable_clauses_mapping(clauses_dict):
    """
    This function returns the mapping of all the clauses involved with any variable
    """
    variable_clause_dict = {}
    variable_clause_dict_full = {}
    for key, value in clauses_dict.items():
        for val in value:
            if val not in variable_clause_dict:
                variable_clause_dict[val] = []
                variable_clause_dict[-val] = []
                variable_clause_dict_full[val] = {}
                variable_clause_dict_full[-val] = {}
            variable_clause_dict[val].append(key)
            variable_clause_dict_full[val][key] = clauses_dict[key]
    return variable_clause_dict, variable_clause_dict_full


def get_clauses_result(clauses_dict, variable_value):
    """
    The function returns list of clauses satisfied and list of clauses unsatisfied based on the current values
    of all the variables
    """
    clauses_satisfied = []
    clauses_not_satisfied = []
    for key, value in clauses_dict.items():
        for val in value:
            if val < 0:
                if not variable_value[abs(val)]:
                    clauses_satisfied.append(key)
                    break
            else:
                if variable_value[val]:
                    clauses_satisfied.append(key)
                    break
        if key not in clauses_satisfied:
            clauses_not_satisfied.append(key)
    return clauses_satisfied, clauses_not_satisfied


def get_negative_gain(variable_value, clauses_satisfied, clauses_dict, unsat_var):
    """
    This function calculated negative gain of any particular unsat variable. It flips that variable and checks the
    new satisfied list and checks how many clauses which were satisfied are now unsatisfied
    """
    variable_value[abs(unsat_var)] = not variable_value[abs(unsat_var)]
    new_clauses_satisfied, new_clauses_not_satisfied = get_clauses_result(clauses_dict, variable_value)
    negative_gain = len(list(set(clauses_satisfied).intersection(new_clauses_not_satisfied)))
    # negative_gain = len(clauses_satisfied) - len(new_clauses_satisfied)
    return negative_gain


def get_variable_negative_gain(variable_value, all_unsatisfied_variables, clauses_satisfied, clauses_dict, variable_clause_dict_all):
    """
    This function is a driver function to negative gain of all the unsat variables. it calls another function and
    claculates and store negative gain of each variable in the dictionary. It also maintains a list of variables which
    have negative gain of 0.
    """
    negative_gain_dict = {}
    zero_list = []
    for unsat_var in all_unsatisfied_variables:
        clauses_dict_new = variable_clause_dict_all[unsat_var]
        clauses_dict_new1 = variable_clause_dict_all[-unsat_var]
        combined_dict = {**clauses_dict_new, **clauses_dict_new1}
        dict_keys = combined_dict.keys()
        filtered_clauses_satisfied = [item for item in clauses_satisfied if item in dict_keys]

        negative_gain = get_negative_gain(
            variable_value,
            filtered_clauses_satisfied,
            combined_dict,
            unsat_var
        )

        negative_gain_dict[unsat_var] = negative_gain
        if negative_gain == 0:
            zero_list.append(unsat_var)
    return negative_gain_dict, zero_list


def select_variable_using_randomwalk(clauses_not_satisfied, clauses_dict):
    """
    This function generates a random number from 0 to length of clauses not satisfied and selects the clause of  that
     index from that list. It again generates other random number and randomly selects variable from that list of
     variables in that clauses
    """
    random_index = random.randint(0, len(clauses_not_satisfied) - 1)
    randomly_selected_clause_variables = clauses_dict[clauses_not_satisfied[random_index]]
    random_index = random.randint(0, len(randomly_selected_clause_variables) - 1)
    value_to_flip = randomly_selected_clause_variables[random_index]
    return value_to_flip


def get_clause_dict(lines):
    """
    This function identifies which are clauses from the lines in instances. If assigns a string C1, C2, C3... Cn to
    all the clauses in the instance file and store them in the dict. For example: {'C1': [1, -2, 3]}
    """
    clauses_dict = {}
    clause_index = 1
    list_of_variables = set()
    for line in lines:
        line = line.strip()
        if len(line) > 1 and line[0] != 'c' and line[0] != 'p' and line != '\n':
            new_list = list(map(int, line.strip()[:-2].split(' ')))
            for var in new_list:
                list_of_variables.add(abs(var))
            clauses_dict['C' + str(clause_index)] = new_list
            clause_index += 1

    list_of_variables = list(list_of_variables)
    return clauses_dict, list_of_variables


def get_total_net_gain(variable_value_temp, clauses_satisfied, clauses_not_satisfied, clauses_dict, unsat_var):
    """
    This function calculates total net gain of each unique variable in the instance file. First the positive gain is
    calculated and then negative gain is calculated. The difference of positive and negative gain is the netgain
    for that variable
    """
    variable_value_temp[abs(unsat_var)] = not variable_value_temp[abs(unsat_var)]
    new_clauses_satisfied, new_clauses_not_satisfied = get_clauses_result(clauses_dict, variable_value_temp)
    # positive_gain = len(list(set(clauses_not_satisfied).intersection(new_clauses_satisfied)))
    # negative_gain = len(list(set(clauses_satisfied).intersection(new_clauses_not_satisfied)))
    positive_gain = len(clauses_not_satisfied) - len(new_clauses_not_satisfied)
    negative_gain = len(clauses_satisfied) - len(new_clauses_satisfied)
    net_gain = positive_gain - negative_gain
    return net_gain


def select_variable_using_gsat_2(clauses_satisfied, clauses_not_satisfied, variable_value_temp, variable_clause_dict_full):
    """
    This function returns a variable to flip using the GSAT method. It calculates netgain of each of the unsat variables
    It selects the variable having highest net-gain. These variable is returned and it will be flipped

    """
    net_gain_dict = {}
    all_unsat_variables = list(variable_value_temp.keys())
    for unsat_var in all_unsat_variables:
        clauses_dict_new = variable_clause_dict_full[unsat_var]
        clauses_dict_new1 = variable_clause_dict_full[-unsat_var]
        combined_dict = {**clauses_dict_new, **clauses_dict_new1}
        dict_keys = combined_dict.keys()
        filtered_clauses_satisfied = [item for item in clauses_satisfied if item in dict_keys]
        filtered_clauses_not_satisfied = [item for item in clauses_not_satisfied if item in dict_keys]

        net_gain_dict[unsat_var] = get_total_net_gain(
            variable_value_temp,
            filtered_clauses_satisfied,
            filtered_clauses_not_satisfied,
            combined_dict,
            unsat_var
        )

    max_value_list = []
    # fetching the maximum net-gain value
    max_value = max(net_gain_dict.items(), key=operator.itemgetter(1))[1]
    # sorts the dict based on the values (net-gain)
    sorted_dict = list(reversed(sorted(net_gain_dict.items(), key=lambda x: x[1])))
    # the below for-loop creates a list of variables having similar maximum net-gain and selects randomly one from them
    for item in sorted_dict:
        if item[1] == max_value:
            max_value_list.append(item[0])
        else:
            break
    random_index = random.randint(0, len(max_value_list) - 1)
    return max_value_list[random_index]
