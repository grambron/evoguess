from datetime import datetime

from pyscipopt import Model

from tools.cnf_to_ilp.cnf import CnfModel


class ScipModel:
    cnf_model: CnfModel = None

    def __init__(self, cnf_model: CnfModel):
        self.model = Model("cnf")
        self.cnf_model: CnfModel = cnf_model

        for i in range(cnf_model.literals_count):
            self.model.addVar(vtype='B', name=str(i))

        for equation in cnf_model.equations:
            expr = 0

            for variable in equation.literals:
                model_var = self.model.getVars()[variable.index - 1]
                assert model_var.name == str(variable.index - 1)

                if variable.sign:
                    expr = expr + model_var
                else:
                    expr = expr + (1 - model_var)

            self.model.addCons(expr >= 1)

        assert len(self.model.getVars()) == self.cnf_model.literals_count

    def measure_optimizing_time(self):
        start_time = datetime.now()
        self.model.optimize()

        return datetime.now() - start_time
