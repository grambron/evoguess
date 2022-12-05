from tools.cnf_to_ilp.cnf_parser.Parser import parse
from tools.cnf_to_ilp.ilp.ScipModel import ScipModel

cnf = parse('cnf_instance/pancake_vs_selection_4_7.cnf')
model = ScipModel(cnf)
time = model.measure_optimizing_time()
print("time: " + str(time))