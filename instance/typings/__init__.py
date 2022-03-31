from .cnf import *
from .gurobi_ilp import *
from . import variables
from .scip_ilp import *
from .scip_ilp_from_cnf import *

types = {
    CNF.slug: CNF,
    GurobiILP.slug: GurobiILP,
    ScipILP.slug: ScipILP,
    ScipILPFromCnf.slug: ScipILPFromCnf,
    **variables.types
}
