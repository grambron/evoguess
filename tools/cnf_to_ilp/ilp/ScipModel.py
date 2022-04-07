from datetime import datetime
from typing import List

from pyscipopt import Model

from tools.cnf_to_ilp.cnf import CnfModel


class ScipModel:
    variables = {}
    cnf_model: CnfModel = None

    def __init__(self, cnf_model: CnfModel):
        self.model = Model(f"cnf")
        self.cnf_model: CnfModel = cnf_model
        self.variables = {}

        counter = 0
        for equation in cnf_model.equations:
            expr = 0
            for variable in equation.literals:
                name = f"x_{variable.name}"
                if name in self.variables:
                    model_var = self.variables[name]
                else:
                    model_var = self.model.addVar(lb=0, ub=1, name=name, vtype='B')
                    self.variables[name] = model_var
                if variable.sign:
                    expr = expr + model_var
                else:
                    expr = expr + (1 - model_var)
            self.model.addCons(expr >= 1, f"constraint_{counter}")
            counter += 1

        assert len(self.model.getVars()) == self.cnf_model.literals_count

    def measure_optimizing_time(self):
        start_time = datetime.now()
        self.model.optimize()

        return datetime.now() - start_time
