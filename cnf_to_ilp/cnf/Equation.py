from typing import List

from cnf_to_ilp.cnf.Variable import Variable


class Equation:
    variables: List[Variable]

    def __init__(self):
        self.variables = []

    def add_variable(self, variable: Variable):
        self.variables.append(variable)
