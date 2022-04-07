from datetime import datetime

from function.module.solver.impl.scip import *
from instance.typings.scip_ilp import ScipILPClause
from tools.cnf_to_ilp.cnf_parser.Parser import parse
from tools.cnf_to_ilp.ilp.ScipModel import ScipModel


def initialize_model():
    # cnf = parse('instances/from_cnf/bubble_vs_pancake_4_7.cnf')
    # model = ScipModel(cnf).model

    model = Model()
    model.readProblem('instances/p2m2p1m1p0n100.mps')
    model.hideOutput()
    model_vars = model.getVars()

    for var_index in backdoor:
        model.chgVarBranchPriority(model_vars[var_index - 1], 1)

    return model


def initialize_backdoor():
    with open('backdoor', 'r') as backdoor_file:
        backdoor_line = backdoor_file.readline()
    return list(map(int, backdoor_line.split()))


if __name__ == '__main__':
    backdoor = initialize_backdoor()
    model = initialize_model()

    time_to_solve = {}
    start_time = datetime.now()
    obj_value = float('inf')

    for i in range(2 ** len(backdoor)):
        assumptions = backdoor.copy()

        for j in range(len(assumptions)):
            if i & 2 ** j != 0:
                assumptions[j] = -assumptions[j]

        status, _ = Scip().propagate(clauses=ScipILPClause(model), assumptions=assumptions)

        if status:
            sol_status, stats, _ = solve_with_variable_substitution(clauses=ScipILPClause(model), assumptions=assumptions)

            time_to_solve[stats['time']] = assumptions

            if sol_status:
                current_obj = model.getSolVal(model.getBestSol(), model.getObjective())
                obj_value = min(obj_value, current_obj)

    with open('solving_statistics', 'w') as solving_stats:
        solving_stats.write("len: " + str(len(time_to_solve)) + "\n")
        solving_stats.write(str(time_to_solve))

    print("Total time: ", datetime.now() - start_time)
    print("Objective: ", obj_value)
