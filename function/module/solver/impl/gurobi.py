from function.module.solver.solver import Solver
from instance.typings.gurobi_ilp import GurobiILPClause

from gurobipy import GRB


class Gurobi(Solver):
    slug = 'solver:gurobi'
    name = 'Solver: Gurobi'

    def solve(self, clauses: GurobiILPClause, assumptions, **kwargs):
        clauses.model.update()
        model = clauses.model.copy()

        for assumption in assumptions:
            if assumption > 0:
                var = model.getVars()[assumption - 1]
                model.addConstr(var >= 1, f"backdoor_assumption_{var}")
                model.addConstr(var <= 1, f"backdoor_assumption_{var}_2")
            else:
                var = model.getVars()[abs(assumption) - 1]
                model.addConstr(var <= 0, f"backdoor_assumption_{var}")

        model.optimize()

        statistics = {'time': model.Runtime}

        status_switcher = {
            GRB.OPTIMAL: True,
            GRB.INFEASIBLE: False,
        }

        return status_switcher.get(model.status), statistics, None
