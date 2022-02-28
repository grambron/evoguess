from tools.cnf_to_ilp.cnf_parser.Parser import parse, parse_backdoor
from tools.cnf_to_ilp.ilp.GurobiModel import GurobiModel
from tools.cnf_to_ilp.ilp.logger.Logger import FileWriterLogger, ConsoleWriterLogger, DisabledLogger
from tools.cnf_to_ilp.ilp.settings import GenerationMode

if __name__ == '__main__':
    with open('solution.txt', 'w') as solution_file, open('gurobi_model.txt', 'w') as gurobi_file:
        solution_file.seek(0)
        gurobi_file.seek(0)
        solution_file.truncate()
        gurobi_file.truncate()

    cnf = parse('../input.lp')
    backdoor = parse_backdoor('backdoor.txt')
    model = GurobiModel(cnf, backdoor)
    model.resolve(GenerationMode.all,
                  solution_logger=FileWriterLogger("solution.txt"),
                  model_logger=FileWriterLogger("gurobi_model.txt"))
