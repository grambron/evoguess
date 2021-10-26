from cnf_to_ilp.cnf.CnfModel import CnfModel
from cnf_to_ilp.cnf.Equation import Equation
from cnf_to_ilp.cnf.Variable import Variable


def parse_line(line) -> Equation:
    equation = Equation()
    for var in line.split():
        if var == "0":
            continue
        abs_var = var
        sign = not var.startswith("-")
        if not sign:
            abs_var = abs_var[1::]
        variable = Variable(abs_var, sign)
        equation.add_variable(variable)
    return equation


def parse(filename: str) -> CnfModel:
    model: CnfModel

    with open(filename) as file:
        first_line = file.readline()
        while first_line.startswith("c"):
            first_line = file.readline()
        variables_count = int(first_line.split()[2])
        # equations_count = first_line[3]
        model = CnfModel(variables_count)

        for line in file:
            if not line.startswith("c"):
                model.add_equation(parse_line(line))

    return model
