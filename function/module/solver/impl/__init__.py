from . import pysat
# from .gurobi import Gurobi
from .pysat import *
from .scip import Scip

solvers = {
    Scip.slug: Scip,
    # Gurobi.slug: Gurobi,
    # Cadical.slug: Cadical,
    # Glucose3.slug: Glucose3,
    # Glucose4.slug: Glucose4,
    # Lingeling.slug: Lingeling,
    # MapleChrono.slug: MapleChrono,
    # MapleCM.slug: MapleCM,
    # MapleSAT.slug: MapleSAT,
    # Minicard.slug: Minicard,
    # Minisat22.slug: Minisat22,
    # MinisatGH.slug: MinisatGH,
}

__all__ = [
    'pysat', 'Scip'
]
