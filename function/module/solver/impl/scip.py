from function.module.solver.solver import Solver
from instance.typings.scip_ilp import ScipILPClause
from pyscipopt.scip import Model


def presolve_and_optimize(model):
    model.presolve()

    if model.getStatus() == "optimal":
        return True, {'time': model.getPresolvingTime()}, None
    elif model.getStatus() == "infeasible":
        return False, {'time': model.getPresolvingTime()}, None

    model.optimize()

    statistics = {'time': model.getSolvingTime()}

    status_switcher = {
        "optimal": True,
        "infeasible": False,
    }

    return status_switcher.get(model.getStatus()), statistics, None


class Scip(Solver):
    slug = 'solver:scip'
    name = 'Solver: SCIP'

    def prototype(self, clauses):
        return ScipWrapper(self, clauses)

    def solve(self, clauses: ScipILPClause, assumptions, **kwargs):
        model = Model(sourceModel=clauses.model, threadsafe=False)

        for var_assumption in assumptions:
            var_index = abs(var_assumption) - 1
            variable = model.getVars()[var_index]

            if var_assumption > 0:
                model.addCons(variable == 1)
            else:
                model.addCons(variable == 0)

        return presolve_and_optimize(model)

    def propagate(self, clauses: ScipILPClause, assumptions, **kwargs):
        model = Model(sourceModel=clauses.model, threadsafe=False)

        for var_assumption in assumptions:
            var_index = abs(var_assumption) - 1
            variable = model.getVars()[var_index]

            if var_assumption > 0:
                model.addCons(variable == 1)
            else:
                model.addCons(variable == 0)

        model.presolve()

        if model.getStatus() == "infeasible":
            return False, {'time': model.getPresolvingTime()}
        else:
            return True, {'time': model.getPresolvingTime()}


class ScipWrapper:

    def __init__(self, solver, clauses):
        self.solver = solver
        self.clauses = clauses

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.solver:
            self.solver = None

    def propagate(self, assumptions):
        return self.solver.propagate(self.clauses, assumptions)
