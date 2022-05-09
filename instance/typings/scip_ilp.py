import os
import re
import threading

from src.pyscipopt.scip import Model
from util.const import TEMPLATE_PATH

ilp_clauses = {}
lock = threading.Lock()
numeral = re.compile('^[-0-9]')


class ScipILPClause:
    def __init__(self, model: Model):
        self.model = model


class ScipILP:
    slug = 'scip_ilp'
    name = 'SCIP_ILP'

    def __init__(self, path):
        self.path = os.path.join(TEMPLATE_PATH, path)

    def _parse(self):
        if self.path in ilp_clauses:
            return

        model = Model()

        model.readProblem(self.path)

        ilp_clauses[self.path] = ScipILPClause(model)

    def clauses(self):
        with lock:
            self._parse()
            return ilp_clauses[self.path]

    def __copy__(self):
        return ScipILP(self.path)

    def __info__(self):
        return {
            'slug': self.slug,
            'name': self.name,
            'path': self.path,
        }


__all__ = [
    'ScipILP'
]
