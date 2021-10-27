from typing import List

from tools.cnf_to_ilp.cnf.Literal import Literal


class Equation:
    literals: List[Literal]

    def __init__(self):
        self.literals = []

    def add_variable(self, variable: Literal):
        self.literals.append(variable)
