from function.module.solver.solver import Solver
from instance.typings.gurobi_ilp import GurobiILPClause

from gurobipy import GRB


class Gurobi(Solver):
    slug = 'solver:gurobi'
    name = 'Solver: Gurobi'

    def solve(self, clauses: GurobiILPClause, assumptions, **kwargs):
        clauses.model.update()
        model = clauses.model.copy()

        for constr in model.getConstrs():
            row = model.getRow(constr)
            row_copy = row.copy()
            rhs = constr.RHS
            model.remove(constr)

            # TODO: probable optimisation point
            # old_vars =  list(map(lambda i: row.getVar(i), range(row.size())))
            # coeffs = list(map(lambda i: row.getCoeff(i), range(row.size())))

            for i in range(row_copy.size()):
                var = row_copy.getVar(i)
                var_index = clauses.var_dict[var.VarName]

                if var_index in assumptions:
                    rhs -= row_copy.getCoeff(i)
                    row.remove(var)
                elif -var_index in assumptions:
                    row.remove(var)

            if constr.sense == '>' or constr.sense == '>=':
                model.addConstr(row >= rhs)
            elif constr.sense == '=':
                model.addConstr(row == rhs)
            elif constr.sense == '<' or constr.sense == '<=':
                model.addConstr(row <= rhs)

        model.optimize()

        statistics = {'time': model.Runtime}

        status_switcher = {
            GRB.OPTIMAL: True,
            GRB.INFEASIBLE: False,
        }
        return status_switcher.get(model.status), statistics, None
