import gurobipy as gp
from gurobipy import GRB

from tools.cnf_to_ilp.cnf.CnfModel import CnfModel


class GurobiModel:
    variables = {}
    cnf_model: CnfModel = None

    def __init__(self, cnf_model: CnfModel):
        self.model = gp.Model("cnf")
        self.cnf_model = cnf_model

        counter = 0
        for equation in cnf_model.equations:
            expr = 0
            for variable in equation.literals:
                name = f"x_{variable.name}"
                if name in self.variables:
                    model_var = self.variables[name]
                else:
                    model_var = self.model.addVar(lb=0, ub=1, name=name, vtype=GRB.INTEGER)
                    self.variables[name] = model_var
                if variable.sign:
                    expr = expr + model_var
                else:
                    expr = expr + (1 - model_var)
            self.model.addConstr(expr >= 1, f"constraint_{counter}")
            counter += 1

    def print_model(self):
        counter = 0
        with open('gurobi_model.txt', 'w') as file:
            for equation in self.cnf_model.equations:
                file.write(f"constraint_{counter}: 0 ")
                for variable in equation.literals:
                    name = f"x_{variable.name}"
                    if variable.sign:
                        file.write(f" + {name} ")
                    else:
                        file.write(f" + (1 - {name}) ")
                file.write(" >= 1\n")
                counter += 1

    def resolve(self):
        self.print_model()

        self.model.optimize()

        self.print_solution()

    def print_solution(self):
        with open('solution.txt', 'w') as file:
            try:
                for var in self.model.getVars():
                    file.write(f" {var.VarName} = {var.x}\n")
            except AttributeError:
                file.write("No solution")
