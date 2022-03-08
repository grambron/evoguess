from function.module.solver.solver import Solver
from instance.typings.scip_ilp import ScipILPClause
from pyscipopt.scip import Model, Row, Expr


class SCIP(Solver):
    slug = 'solver:scip'
    name = 'Solver: SCIP'

    def solve(self, clauses: ScipILPClause, assumptions, **kwargs):
        model = Model(sourceModel=clauses.model, threadsafe=True)

        for var_assumption in assumptions:
            var_index = abs(var_assumption) - 1
            variable = model.getVars()[var_index]

            if var_assumption > 0:
                model.addCons(variable == 1)
            else:
                model.addCons(variable == 0)

        model.presolve()

        if model.getStatus() == "optimal":
            return True, {'time': model.getSolvingTime()}, None
        elif model.getStatus() == "infeasible":
            return False, {'time': model.getSolvingTime()}, None

        model.optimize()

        statistics = {'time': model.getSolvingTime()}

        status_switcher = {
            "optimal": True,
            "infeasible": False,
        }

        return status_switcher.get(model.getStatus()), statistics, None
