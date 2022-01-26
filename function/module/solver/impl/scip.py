from function.module.solver.solver import Solver
from instance.typings.scip_ilp import ScipILPClause
from pyscipopt.scip import Model


class SCIP(Solver):
    slug = 'solver:scip'
    name = 'Solver: SCIP'

    def solve(self, clauses: ScipILPClause, assumptions, **kwargs):
        model = Model(sourceModel=clauses.model, origcopy=True)

        for assumption in assumptions:
            if assumption > 0:
                var = model.getVars()[assumption - 1]
                model.addCons(var >= 1, f"backdoor_assumption_{var}")
                model.addCons(var <= 1, f"backdoor_assumption_{var}_2")
            else:
                var = model.getVars()[abs(assumption) - 1]
                model.addCons(var <= 0, f"backdoor_assumption_{var}")

        model.optimize()

        statistics = {'time': model.getSolvingTime()}

        status_switcher = {
            "optimal": True,
            "infeasible": False,
        }

        return status_switcher.get(model.getStatus()), statistics, None
