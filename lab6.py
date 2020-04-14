import random
import sys
random.seed('183334')


def get_clauses_result(clauses_dict, variable_value):
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


def get_not_satisfied_clause_var(clauses_dict, clauses_not_satisfied):
    unique_variables = []
    for clause in clauses_not_satisfied:
        unique_variables.extend(clauses_dict[clause])
    return list(set(unique_variables))


def main(f, max_flips=1, max_tries=1):
    clauses_dict = {}
    clause_index = 1
    list_of_variables = []
    for line in f.readlines():
        line = line.strip()
        if len(line) > 1 and line[0] != 'c' and line[0] != 'p' and line != '\n':
            new_list = list(map(int, line.strip()[:-2].split(' ')))
            list_of_variables.extend(new_list)
            clauses_dict['C' + str(clause_index)] = new_list

            clause_index += 1
    variable_value = {}
    list_of_variables = list(set(list_of_variables))
    for variable in list_of_variables:
        if variable > 0:
            variable_value[variable] = True
        else:
            variable_value[abs(variable)] = False
            # print(variable_value)
    for max_index in range(max_tries):
        for flip_index in range(max_flips):
            clauses_satisfied, clauses_not_satisfied = get_clauses_result(clauses_dict, variable_value)
            if len(clauses_satisfied) == len(clauses_dict.keys()):
                print('Number of restarts', max_index)
                print('Number of flips in current restart', flip_index)
                return variable_value
            list_not_sat_vars = get_not_satisfied_clause_var(clauses_dict, clauses_not_satisfied)
            random_index = random.randint(0, len(list_not_sat_vars)-1)
            value_to_flip = list_not_sat_vars[random_index]
            if value_to_flip < 0:
                value_to_flip = abs(value_to_flip)
            variable_value[value_to_flip] = not variable_value[value_to_flip]
    return False


if __name__ == '__main__':
    input_file = sys.argv[1]
    # output_file = sys.argv[2]
    f = open(input_file, 'r')
    result = main(f, 100, 100)
    if result:
        final_ouput_list = [key if value else key * -1 for key, value in result.items()]
        print('Solution-->', final_ouput_list)
        print()
    else:
        print('Solution not found')
