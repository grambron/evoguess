import re
import threading

from pyscipopt.scip import Model


ilp_clauses = {}
lock = threading.Lock()
numeral = re.compile('^[-0-9]')


class ScipILPClause:
    def __init__(self, model: Model):
        self.model = model


class ScipILPClauseForValidation:
    def __init__(self, model: Model):
        self.model = model
        self.var_index_dict = {}

        counter = 1
        for var in model.getVars():
            self.var_index_dict[var.name] = counter
            counter += 1


class ScipILP:
    slug = 'scip_ilp'
