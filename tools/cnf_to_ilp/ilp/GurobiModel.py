import random

import gurobipy as gp
from gurobipy import GRB
import time

from tools.cnf_to_ilp.cnf.CnfModel import CnfModel
from tools.cnf_to_ilp.ilp.settings import GENERATION_BACKDOOR_VALUES_COUNT, GENERATION_MODE


class GurobiModel:
    variables = {}
    cnf_model: CnfModel = None
    possible_backdoors_count: int
    proceed_backdoor_values: set

    def __init__(self, cnf_model: CnfModel, backdoor: list[str]):
        self.model = gp.Model("cnf")
        self.cnf_model: CnfModel = cnf_model
        self.backdoor: list[str] = backdoor

        self.possible_backdoors_count = 2 ** len(self.backdoor)
        self.proceed_backdoor_values = set()

        self.model.setParam('OutputFlag', False)

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

    def print_model(self, file):
        counter = 0
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

    def print_solution(self, file, backdoor_value: dict, execution_time):
        file.write(str(backdoor_value) + "\n")
        file.write("--- %s seconds ---\n" % execution_time)
        try:
            for var in self.model.getVars():
                file.write(f"{var.x}, ")
        except AttributeError:
            file.write("No solution")
        file.write("\n")

    def choose_backdoor_variant(self):
        current_variant = random.randint(0, self.possible_backdoors_count)
        while current_variant in self.proceed_backdoor_values:
            current_variant = random.randint(0, self.possible_backdoors_count)
        self.proceed_backdoor_values.add(current_variant)
        return current_variant

    def resolve(self):
        if GENERATION_MODE == "CERTAIN_NUMBER_OF_GENERATIONS":
            self.resolve_for_certain_number_of_generations()
        else:
            self.resolve_for_all()

    def resolve_for_certain_backdoor(self, backdoor_value, gurobi_model_file, solution_file):
        self.print_model_with_backdoor_constraints(gurobi_model_file, backdoor_value)

        self.add_backdoor_constraints(backdoor_value)

        start_time = time.time()
        self.model.optimize()
        self.print_solution(solution_file, backdoor_value, time.time() - start_time)

        self.model.remove(self.model.getConstrs()[-len(self.backdoor)::])
        self.model.reset()

    def print_model_with_backdoor_constraints(self, file, backdoor_value):
        self.print_model(file)

        backdoor_counter = 0
        for variable in backdoor_value.items():
            name = f"x_{variable[0]}"
            variable_value = variable[1]
            file.write(f"backdoor_constraint_{backdoor_counter}: ")
            if variable_value == 0:
                file.write(f"{name} <= 0\n")
            else:
                file.write(f"{name} >= 1\n")
            backdoor_counter += 1
        file.write("\n")

    def add_backdoor_constraints(self, backdoor_value):
        counter = 0
        for variable in backdoor_value.items():
            name = f"x_{variable[0]}"
            model_var = self.variables[name]
            variable_value = variable[1]
            if variable_value == 0:
                self.model.addConstr(model_var <= 0, f"backdoor_constraint_{counter}")
            else:
                self.model.addConstr(model_var >= 1, f"backdoor_constraint_{counter}")
            counter += 1

    def resolve_for_certain_number_of_generations(self):
        with open('solution.txt', 'a') as solution_file, open('gurobi_model.txt', 'a') as gurobi_model_file:
            for _ in range(0, GENERATION_BACKDOOR_VALUES_COUNT):
                if len(self.proceed_backdoor_values) == self.possible_backdoors_count:
                    break

                variant = self.choose_backdoor_variant()

                backdoor_value = {}
                for i in range(0, len(self.backdoor)):
                    backdoor_value[self.backdoor[i]] = 1 if (variant & 2 ** i != 0) else 0

                self.resolve_for_certain_backdoor(backdoor_value, gurobi_model_file, solution_file)

    def resolve_for_all(self):
        with open('solution.txt', 'a') as solution_file, open('gurobi_model.txt', 'a') as gurobi_model_file:
            for variant in range(0, self.possible_backdoors_count):
                backdoor_value = {}
                for i in range(0, len(self.backdoor)):
                    backdoor_value[self.backdoor[i]] = 1 if (variant & 2 ** i != 0) else 0
                self.resolve_for_certain_backdoor(backdoor_value, gurobi_model_file, solution_file)
