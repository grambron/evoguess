from datetime import datetime

from pyscipopt.scip import Model

from function.module.solver.impl import Scip
from instance.typings.scip_ilp import ScipILPClause


def initialize_model():
    model.hideOutput()
    model.readProblem('bnatt500.mps')

    model_vars = model.getVars()

    for var_index in backdoor:
        model.chgVarBranchPriority(model_vars[var_index - 1], 1)


def initialize_backdoor():
    with open('backdoor', 'r') as backdoor_file:
        backdoor_line = backdoor_file.readline()
    return list(map(int, backdoor_line.split()))


if __name__ == '__main__':
    backdoor = initialize_backdoor()
    model = Model()
    initialize_model()

    time_to_solve = {}
    start_time = datetime.now()

    for i in range(2 ** len(backdoor)):
        assumptions = backdoor.copy()

        for j in range(len(assumptions)):
            if i & 2 ** j != 0:
                assumptions[j] = -assumptions[j]

        status, _ = Scip().propagate(clauses=ScipILPClause(model), assumptions=assumptions)

        if status:
            sol_status, stats, _ = Scip().solve(clauses=ScipILPClause(model), assumptions=assumptions)
            time_to_solve[stats['time']] = assumptions

    with open('solving_statistics', 'w') as solving_stats:
        solving_stats.write("len: " + str(len(time_to_solve)) + "\n")
        solving_stats.write(str(time_to_solve))

    print("total time: ", datetime.now() - start_time)
