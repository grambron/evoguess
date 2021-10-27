from typing import *

from tools.cnf_to_ilp.cnf.Equation import Equation


class CnfModel:
    equations: List[Equation]
    literals_count: int = 0

    def __init__(self, variables_count: int):
        self.literals_count = variables_count
        self.equations = []

    def add_equation(self, equation: Equation):
        self.equations.append(equation)
