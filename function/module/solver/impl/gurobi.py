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
            rhs = constr.RHS
            model.remove(constr)

            for i in range(row.size()):
                var = row.getVar(i).VarName
                var_index = clauses.var_dict[var]

                if var_index in assumptions:
                    rhs -= row.getCoeff(i)
                    row.remove(var)
                elif -var_index in assumptions:
                    row.remove(var)

                if constr.sense == '>':
                    model.addConstr(row > rhs)
                elif constr.sense == '=':
                    model.addConstr(row == rhs)
                elif constr.sense == '<':
                    model.addConstr(row < rhs)
                elif constr.sense == '<=':
                    model.addConstr(row <= rhs)
                elif constr.sense == '>=':
                    model.addConstr(row >= rhs)

            model.optimize()

            statistics = {'time': model.Runtime}

            status_switcher = {
                GRB.OPTIMAL: True,
                GRB.INFEASIBLE: False,
            }
            return status_switcher.get(model.status), statistics, None
