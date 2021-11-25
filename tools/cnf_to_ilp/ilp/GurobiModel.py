import random
import time
from typing import List

import gurobipy as gp
from gurobipy import GRB

from tools.cnf_to_ilp.cnf.CnfModel import CnfModel
from tools.cnf_to_ilp.ilp.logger.Logger import Logger, DisabledLogger
from tools.cnf_to_ilp.ilp.settings import GENERATION_BACKDOOR_VALUES_COUNT, GenerationMode


class GurobiModel:
    variables = {}
    cnf_model: CnfModel = None
    possible_backdoors_count: int
    proceed_backdoor_values: set
    solution_logger: Logger
    model_logger: Logger

    def __init__(self, cnf_model: CnfModel, backdoor: List[str]):
        self.model = gp.Model(f"cnf")
        self.cnf_model: CnfModel = cnf_model
        self.backdoor: List[str] = backdoor
        self.variables = {}

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

    def print_model(self):
        counter = 0
        for equation in self.cnf_model.equations:
            self.model_logger.write(f"constraint_{counter}: 0 ")
            for variable in equation.literals:
                name = f"x_{variable.name}"
                if variable.sign:
                    self.model_logger.write(f" + {name} ")
                else:
                    self.model_logger.write(f" + (1 - {name}) ")
            self.model_logger.write(" >= 1\n")
            counter += 1

    def make_solution(self, backdoor_value: dict) -> bool:
        start_time = time.time()
        self.model.optimize()
        time_for_certain_backdoor_values = time.time() - start_time

        self.solution_logger.write(str(backdoor_value) + "\n")
        self.solution_logger.write("--- %s seconds ---\n" % time_for_certain_backdoor_values)

        try:
            for var in self.model.getVars():
                self.solution_logger.write(f"{var.x}, ")
        except AttributeError:
            self.solution_logger.write("No solution\n")
            return False
        self.solution_logger.write("\n")
        return True

    def make_random_variant(self):
        current_variant = random.randint(0, self.possible_backdoors_count)
        while current_variant in self.proceed_backdoor_values:
            current_variant = random.randint(0, self.possible_backdoors_count)
        self.proceed_backdoor_values.add(current_variant)
        return current_variant

    def resolve(self, mode: GenerationMode, solution_logger=DisabledLogger(), model_logger=DisabledLogger()) -> bool:
        self.solution_logger = solution_logger
        self.model_logger = model_logger

        if mode == GenerationMode.certain:
            result = self.resolve_for_certain_number_of_generations()
        elif mode == GenerationMode.all:
            result = self.resolve_for_all()
        else:
            solution_logger.close()
            model_logger.close()
            raise ValueError("Illegal generation mode in settings.py")

        solution_logger.close()
        model_logger.close()
        return result

    def resolve_for_certain_number_of_generations(self) -> bool:
        result_time = 0
        start_time = time.time()

        for i in range(0, GENERATION_BACKDOOR_VALUES_COUNT):
            if len(self.proceed_backdoor_values) == self.possible_backdoors_count:
                break

            variant = self.make_random_variant()

            backdoor_value = {}
            for j in range(0, len(self.backdoor)):
                backdoor_value[self.backdoor[j]] = 1 if (variant & 2 ** j != 0) else 0

            solution = self.resolve_for_certain_backdoor_values(backdoor_value)

            if solution:
                result_time += time.time() - start_time
                self.solution_logger.write(f"result time: {result_time}")
                return True

        result_time += time.time() - start_time
        self.solution_logger.write(f"result time: {result_time}")
        return False

    def resolve_for_all(self) -> bool:
        result_time = 0

        start_time = time.time()
        for variant in range(0, self.possible_backdoors_count):
            backdoor_value = {}
            for i in range(0, len(self.backdoor)):
                backdoor_value[self.backdoor[i]] = 1 if (variant & 2 ** i != 0) else 0

            solution = self.resolve_for_certain_backdoor_values(backdoor_value)

            if solution:
                result_time += time.time() - start_time
                self.solution_logger.write(f"result time: {result_time}")
                return True

        result_time += time.time() - start_time
        self.solution_logger.write(f"result time: {result_time}")
        return False

    def resolve_for_certain_backdoor_values(self, backdoor_value) -> bool:
        self.print_model_with_backdoor_constraints(backdoor_value)

        self.add_backdoor_constraints(backdoor_value)

        solution = self.make_solution(backdoor_value)

        self.model.remove(self.model.getConstrs()[-len(self.backdoor)::])
        self.model.reset()

        return solution

    def print_model_with_backdoor_constraints(self, backdoor_value):
        self.print_model()

        backdoor_counter = 0
        for variable in backdoor_value.items():
            name = f"x_{variable[0]}"
            variable_value = variable[1]
            self.model_logger.write(f"backdoor_constraint_{backdoor_counter}: ")
            if variable_value == 0:
                self.model_logger.write(f"{name} <= 0\n")
            else:
                self.model_logger.write(f"{name} >= 1\n")
            backdoor_counter += 1
        self.model_logger.write("\n")

    def add_backdoor_constraints(self, backdoor_value):
        counter = 0
        for variable in backdoor_value.items():
            name = f"x_{variable[0]}"
            try:
                model_var = self.variables[name]
            except KeyError:
                raise ValueError("More literals in backdoor than in formula")
            variable_value = variable[1]
            if variable_value == 0:
                self.model.addConstr(model_var <= 0, f"backdoor_constraint_{counter}")
            else:
                self.model.addConstr(model_var >= 1, f"backdoor_constraint_{counter}")
            counter += 1
