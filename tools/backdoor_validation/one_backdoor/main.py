import argparse
import sys

from src.pyscipopt.scip import Model

# sys.path.append('/mnt/tank/scratch/abadikova/evoguess-fw/evoguess')

from datetime import datetime

from tools.cnf_to_ilp.cnf_parser.Parser import parse
from tools.cnf_to_ilp.ilp.ScipModel import ScipModel


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--instance_format', nargs='?', type=str, help='ilp or cnf')
    parser.add_argument('-f', '--file', nargs='?', type=str, help='file name')
    namespace = parser.parse_args(sys.argv[1:])

    file_name = namespace.file
    instance = namespace.instance_format

    if instance != 'cnf' and instance != 'ilp':
        raise Exception("illegal instance format. Input 'ilp' or 'cnf'.")

    return instance, file_name


def initialize_model(instance_format, file):
    if instance_format == 'cnf':
        cnf = parse(file)
        new_model = ScipModel(cnf).model
    else:
        new_model = Model()
        new_model.readProblem(file)

    new_model.hideOutput()

    return new_model


def initialize_backdoor():
    # with open('backdoor', 'r') as backdoor_file:
    #     backdoor_line = backdoor_file.readline()
    backdoor_line = "98 222 266 417 447 454 742 1334 1711 2130 2488 2516"
    return list(map(int, backdoor_line.split()))


if __name__ == '__main__':
    backdoor = initialize_backdoor()
    instance_format, file = parse_arguments()
    model = initialize_model(instance_format, file)

    start_time = datetime.now()
    obj_value = float('inf')

    for i in range(2 ** len(backdoor)):
        print(i)
        assumptions = backdoor.copy()

        for j in range(len(assumptions)):
            if i & 2 ** j != 0:
                assumptions[j] = -assumptions[j]

        status, _ = model.propagate_by_presolve(assumptions)

        if status:
            var_index_dict = {}

            counter = 1
            for var in model.getVars():
                var_index_dict[var.name] = counter
                counter += 1

            sol_status, stats, current_obj = model.solve_with_variable_substitution(var_index_dict, assumptions)

            if sol_status:
                obj_value = min(obj_value, current_obj)

    print("Total time: ", datetime.now() - start_time)
    print("Objective: ", obj_value)
