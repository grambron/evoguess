# from function.module.solver.solver import Solver
# from instance.typings.gurobi_ilp import GurobiILPClause
#
# from gurobipy import GRB
#
#
# class Gurobi(Solver):
#     slug = 'solver:gurobi'
#     name = 'Solver: Gurobi'
#
#     def solve(self, clauses: GurobiILPClause, assumptions, **kwargs):
#         model = clauses.model.copy()
#
#         for var_assumption in assumptions:
#             var_index = abs(var_assumption) - 1
#             variable = model.getVars()[var_index]
#
#             if var_assumption > 0:
#                 model.addConstr(variable == 1)
#             else:
#                 model.addConstr(variable == 0)
#
#         # try:
#         #     p = model.presolve()
#         #     print("status: ", p.status)
#         # except Exception as e:
#         #     pass
#
#         model.optimize()
#
#         statistics = {'time': model.Runtime}
#
#         status_switcher = {
#             GRB.OPTIMAL: True,
#             GRB.INFEASIBLE: False,
#         }
#
#         return status_switcher.get(model.status), statistics, None
