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
                    new_constr += clauses.var_dict[var_name] * vars_in_constr_map[var_name]

            model.delCons(constr)

            if rhs > lhs:
                model.addCons(new_constr <= bound)
            elif lhs > rhs:
                model.addCons(new_constr >= bound)
            else:
                model.addCons(new_constr == bound)

        model.optimize()

        statistics = {'time': model.getSolvingTime()}

        status_switcher = {
            "optimal": True,
            "infeasible": False,
        }

        return status_switcher.get(model.getStatus()), statistics, None
