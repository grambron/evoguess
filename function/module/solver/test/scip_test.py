import unittest
from pyscipopt.scip import Model

from function.module.solver.impl import SCIP
from instance.typings.scip_ilp import ScipILPClause


class MyTestCase(unittest.TestCase):
    def test_with_optimal_all_variables_in_assumptions(self):
        assumptions = [1, -2]

        clauses = initialize_base_clauses()

        status, stats, _ = SCIP().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(status, True)

    def test_with_infeasible_all_variables_in_assumptions(self):
        assumptions = [1, 2]

        clauses = initialize_base_clauses()

        status, stats, _ = SCIP().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(status, False)

    def test_optimal_one_variable_in_assumptions(self):
        assumptions = [-1]

        clauses = initialize_base_clauses()

        status, stats, _ = SCIP().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(status, True)

    def test_infeasible_one_variable_in_assumptions(self):
        assumptions = [-2]
        model = Model()

        x = model.addVar(vtype='B', name='X')
        y = model.addVar(vtype='B', name='Y')
        model.addCons(x + y >= 1)
        model.addCons(x == 0)
        clauses = ScipILPClause(model)

        status, stats, _ = SCIP().solve(clauses=clauses, assumptions=assumptions)
        self.assertEqual(False, status)


def initialize_base_clauses():
    model = Model()

    x = model.addVar(vtype='B', name='X')
    y = model.addVar(vtype='B', name='Y')

    model.addCons(x + y <= 1)

    return ScipILPClause(model)


if __name__ == '__main__':
    unittest.main()
