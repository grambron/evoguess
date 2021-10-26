from typing import *

from cnf_to_ilp.cnf.Equation import Equation


class CnfModel:
    equations: List[Equation]
    variables_count: int = 0

    def __init__(self, variables_count: int):
        self.variables_count = variables_count
        self.equations = []

    def add_equation(self, equation: Equation):
        self.equations.append(equation)
