import unittest
from gurobipy import Model

from function.module.solver.impl import Gurobi
from instance.typings.gurobi_ilp import GurobiILPClause


class GurobiTestCases(unittest.TestCase):

    def test_with_optimal_all_variables_in_assumptions(self):
        assumptions = [1, -2]

        clauses = initialize_base_clauses()

        status, stats, _ = Gurobi().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(status, True)

    def test_with_infeasible_all_variables_in_assumptions(self):
        assumptions = [1, 2]

        clauses = initialize_base_clauses()

        status, stats, _ = Gurobi().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(status, False)

    def test_optimal_one_variable_in_assumptions(self):
        assumptions = [1]

        clauses = initialize_base_clauses()

        status, stats, _ = Gurobi().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(status, True)

    def test_infeasible_one_variable_in_assumptions(self):
        assumptions = [-2]
        model = Model()

        x = model.addVar(vtype='B', name='X')
        y = model.addVar(vtype='B', name='Y')
        model.addConstr(x + y >= 1)
        model.addConstr(x == 0)
        model.update()
        clauses = GurobiILPClause(model)

        status, stats, _ = Gurobi().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(status, False)


def initialize_base_clauses():
    model = Model()

    x = model.addVar(vtype='B', name='X')
    y = model.addVar(vtype='B', name='Y')

    model.addConstr(x + y <= 1)
    model.update()

    return GurobiILPClause(model)


if __name__ == '__main__':
    unittest.main()
