from function.module.solver.solver import Solver
from instance.typings.scip_ilp import ScipILPClause
from pyscipopt.scip import Model, Row, Expr


class SCIP(Solver):
    slug = 'solver:scip'
    name = 'Solver: SCIP'

    def solve(self, clauses: ScipILPClause, assumptions, **kwargs):
        model = Model(sourceModel=clauses.model, threadsafe=True)

        for constr in model.getConss():
            vars_in_constr_map = model.getValsLinear(constr)

            rhs = model.getRhs(constr)
            lhs = model.getLhs(constr)

            bound = min(abs(rhs), abs(lhs))
            new_constr = Expr()

            for var_name in vars_in_constr_map.keys():
                var_index = clauses.var_index_dict[var_name]

                if var_index in assumptions:
                    bound -= vars_in_constr_map[var_name]
                elif -var_index not in assumptions:
                    assert model.getVars()[var_index - 1].name == clauses.model.getVars()[var_index - 1].name
                    new_constr += model.getVars()[var_index - 1] * vars_in_constr_map[var_name]

            if lhs != rhs:
                if lhs == -1e20:
                    model.addCons(new_constr <= bound)
                elif rhs == 1e20:
                    model.addCons(new_constr >= bound)
                else:
                    raise Exception("illegal sign in constraint")
            else:
                model.addCons(new_constr == bound)

            model.delCons(constr)

        model.presolve()

        if model.getStatus() == "optimal":
            return True, {'time': 0.0}, None
        elif model.getStatus() == "infeasible":
            return False, {'time': 0.0}, None

        model.optimize()

        statistics = {'time': model.getSolvingTime()}

        status_switcher = {
            "optimal": True,
            "infeasible": False,
        }

        return status_switcher.get(model.getStatus()), statistics, None
