from datetime import datetime

from pyscipopt.scip import Model

from function.module.solver.impl import Scip
from instance.typings.scip_ilp import ScipILPClause

if __name__ == '__main__':
    with open('backdoor', 'r') as backdoor_file, open('input.lp', 'r') as instance:
        line = backdoor_file.readline()
        backdoor = list(map(int, line.split()))

        model = Model()
        model.readProblem(instance)

        start_time = datetime.now()

        for i in range(2 ** len(backdoor)):
            assumptions = backdoor.copy()

            for j in range(len(assumptions)):
                if i & 2 ** j != 0:
                    assumptions[j] = -assumptions[j]

            status, stats = Scip().propagate(clauses=ScipILPClause(model), assumptions=assumptions)

            if status != "optimal":
                model.solve()

        print("total time: ", datetime.now() - start_time)
