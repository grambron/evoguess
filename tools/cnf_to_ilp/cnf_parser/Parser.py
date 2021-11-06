from tools.cnf_to_ilp.cnf.CnfModel import CnfModel
from tools.cnf_to_ilp.cnf.Equation import Equation
from tools.cnf_to_ilp.cnf.Literal import Literal


def parse_line(line) -> Equation:
    equation = Equation()
    for var in line.split():
        if var == "0":
            continue
        abs_var = var
        sign = not var.startswith("-")
        if not sign:
            abs_var = abs_var[1::]
        variable = Literal(abs_var, sign)
        equation.add_variable(variable)
    return equation


def parse(filename: str) -> CnfModel:
    model: CnfModel

    with open(filename) as file:
        first_line = file.readline()
        while first_line.startswith("c"):
            first_line = file.readline()

        literals_count = int(first_line.split()[2])
        # equations_count = first_line[3]
        model = CnfModel(literals_count)

        for line in file:
            if not line.startswith("c"):
                model.add_equation(parse_line(line))

    return model


def parse_backdoor(backdoor_file: str) -> list[str]:
    with open(backdoor_file) as file:
        backdoor = file.readline().split()

    return backdoor
