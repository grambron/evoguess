# import os
# import re
# import threading
#
# import gurobipy
# from gurobipy import read
#
# from util.const import TEMPLATE_PATH
#
# ilp_clauses = {}
# lock = threading.Lock()
# numeral = re.compile('^[-0-9]')
#
#
# class GurobiILPClause:
#     def __init__(self, model: gurobipy.Model):
#         self.model = model
#
#         self.var_dict = {}
#         counter = 1
#         for var in model.getVars():
#             self.var_dict[var.VarName] = counter
#             counter += 1
#
#
# class GurobiILP:
#     slug = 'gurobi_ilp'
#     name = 'Gurobi_ILP'
#
#     def __init__(self, path):
#         self.path = os.path.join(TEMPLATE_PATH, path)
#
#     def _parse(self):
#         if self.path in ilp_clauses:
#             return
#
#         model = read(self.path)
#
#         ilp_clauses[self.path] = GurobiILPClause(model)
#
#     def clauses(self):
#         with lock:
#             self._parse()
#             return ilp_clauses[self.path]
#
#     def __copy__(self):
#         return GurobiILP(self.path)
#
#     def __info__(self):
#         return {
#             'slug': self.slug,
#             'name': self.name,
#             'path': self.path,
#         }
#
#
# __all__ = [
#     'GurobiILP'
# ]
