import itertools
from datetime import datetime
import sys

# sys.path.append('/mnt/tank/scratch/abadikova/evoguess-fw/evoguess')

from tools.backdoor_validation.one_backdoor.main import parse_arguments, initialize_model


def initialize_backdoors():
    input_backdoors = []

    with open('backdoors', 'r') as backdoor_file:
        for line in backdoor_file:
            input_backdoors.append(list(map(int, line.split())))

    return input_backdoors


if __name__ == '__main__':
    backdoors = initialize_backdoors()
    instance_format, file = parse_arguments()
    model = initialize_model(instance_format, file)

    obj_value = float('inf')
    all_assumptions_to_solve = []
    start_time = datetime.now()

    for backdoor in backdoors:
        assumptions_to_solve = []

        for i in range(2 ** len(backdoor)):
            assumptions = backdoor.copy()

            # assumption value generation
            for j in range(len(assumptions)):
                if i & 2 ** j != 0:
                    assumptions[j] = -assumptions[j]

            status, _ = model.propagate_by_presolve(assumptions)

            if status:
                assumptions_to_solve.append(assumptions)

        all_assumptions_to_solve.append(assumptions_to_solve)

    for cortege in itertools.product(*all_assumptions_to_solve):
        assumptions = set(cortege[0] + cortege[1])
        print(assumptions)

        var_index_dict = {}

        counter = 1
        for var in model.getVars():
            var_index_dict[var.name] = counter
            counter += 1

        sol_status, stats, current_obj = model.solve_with_variable_substitution(assumptions)

        if sol_status:
            obj_value = min(obj_value, current_obj)

    print("Total time: ", datetime.now() - start_time)
    print("Objective: ", obj_value)


