from cnf_to_ilp.cnf_parser.Parser import parse
from cnf_to_ilp.ilp.GurobiModel import GurobiModel

if __name__ == '__main__':
    cnf = parse('../input.txt')
    model = GurobiModel(cnf)
    model.resolve()
