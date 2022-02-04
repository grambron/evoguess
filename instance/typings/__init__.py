from .cnf import *
from .gurobi_ilp import *
from . import variables
# from .scip_ilp import ScipILP

types = {
    CNF.slug: CNF,
    GurobiILP.slug: GurobiILP,
    # ScipILP.slug: ScipILP,
    **variables.types
}
