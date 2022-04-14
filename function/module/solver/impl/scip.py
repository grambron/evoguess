from function.module.solver.solver import Solver
from instance.typings.scip_ilp import ScipILPClause
from pyscipopt.scip import Model, Row, Expr


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


def solve_with_variable_substitution(clauses: ScipILPClause, assumptions):
    model = Model(sourceModel=clauses.model, threadsafe=False)

    for constr in model.getConss():
        vars_in_constr_map = model.getValsLinear(constr)

        rhs = model.getRhs(constr)
        lhs = model.getLhs(constr)
        double_inequity = (lhs != rhs) and (lhs > -1e20) and (rhs < 1e20)
        bound = min(abs(rhs), abs(lhs))

        new_constr = Expr()

        for var_name in vars_in_constr_map.keys():
            var_index = clauses.var_index_dict[var_name]

            if var_index in assumptions:
                if not double_inequity:
                    bound -= vars_in_constr_map[var_name]
                else:
                    rhs -= vars_in_constr_map[var_name]
                    lhs -= vars_in_constr_map[var_name]
            elif -var_index not in assumptions:
                assert model.getVars()[var_index - 1].name == clauses.model.getVars()[var_index - 1].name
                new_constr += model.getVars()[var_index - 1] * vars_in_constr_map[var_name]

        if lhs != rhs:
            if lhs <= -1e20:
                model.addCons(new_constr <= bound)
            elif rhs >= 1e20:
                model.addCons(new_constr >= bound)
            elif double_inequity:
                model.addCons((rhs >= new_constr) >= lhs)
            else:
                raise Exception("illegal sign in constraint")
        else:
            model.addCons(new_constr == bound)

        model.delCons(constr)

    model.optimize()

    if model.getStatus() == "optimal":
        return True, {'time': model.getSolvingTime()}, None
    elif model.getStatus() == "infeasible":
        return False, {'time': model.getSolvingTime()}, None


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

    def propagate(self, assumptions, **kwargs):
        return self.solver.propagate(self.clauses, assumptions)
