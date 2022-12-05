import os
import re
import threading

from pyscipopt.scip import PY_SCIP_PARAMSETTING

from instance.typings.scip_ilp import ScipILPClause
from tools.cnf_to_ilp.cnf_parser.Parser import parse
from tools.cnf_to_ilp.ilp.ScipModel import ScipModel
from util.const import TEMPLATE_PATH

ilp_clauses = {}
lock = threading.Lock()
numeral = re.compile('^[-0-9]')


class ScipILPFromCnf:
    slug = 'scip_ilp_from_cnf'
    name = 'SCIP_ILP_FROM_CNF'

    def __init__(self, path):
        self.path = os.path.join(TEMPLATE_PATH, path)

    def _parse(self):
        if self.path in ilp_clauses:
            return

        cnf = parse(self.path)
        scip_model = ScipModel(cnf).model

        scip_model.hideOutput()

        scip_model.setPresolve(PY_SCIP_PARAMSETTING.AGGRESSIVE)
        scip_model.presolve()
        scip_model.setPresolve(PY_SCIP_PARAMSETTING.DEFAULT)

        ilp_clauses[self.path] = ScipILPClause(scip_model)

    def clauses(self):
        with lock:
            self._parse()
            return ilp_clauses[self.path]

    def __copy__(self):
        return ScipILPFromCnf(self.path)

    def __info__(self):
        return {
            'slug': self.slug,
            'name': self.name,
            'path': self.path,
        }


__all__ = [
    'ScipILPFromCnf'
]
