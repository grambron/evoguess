import argparse

from datetime import datetime

from function.module.solver.impl.scip import *
from instance.typings.scip_ilp import ScipILPClause
from tools.cnf_to_ilp.cnf_parser.Parser import parse
from tools.cnf_to_ilp.ilp.ScipModel import ScipModel


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--instance_format', nargs='?', type=str, help='ilp or cnf')
    parser.add_argument('-f', '--file', nargs='?', type=str, help='file name')
    namespace = parser.parse_args(sys.argv[1:])

    file_name = namespace.file
    instance = namespace.instance_format

    if instance != 'cnf' and instance != 'ilp':
        raise Exception("illegal instance format. Input 'ilp' or 'cnf'.")

    return instance, file_name


def initialize_model(instance_format, file):
    if instance_format == 'cnf':
        cnf = parse(file)
        new_model = ScipModel(cnf).model
    else:
        new_model = Model()
        new_model.readProblem(file)

    new_model.hideOutput()

    return new_model


def initialize_backdoor():
    with open('backdoor', 'r') as backdoor_file:
        backdoor_line = backdoor_file.readline()
    return list(map(int, backdoor_line.split()))


def add_single_inequality(lhs, rhs, bound, new_constr, model):
    if lhs <= -1e20:
        model.addCons(new_constr <= bound)
    elif rhs >= 1e20:
        model.addCons(new_constr >= bound)
    else:
        raise Exception("illegal sign in constraint")


def solve_with_variable_substitution(clauses: ScipILPClauseForValidation, assumptions):
    model = Model(sourceModel=clauses.model)

    for constr in model.getConss():
        vars_in_constr_map = model.getValsLinear(constr)

        rhs = model.getRhs(constr)
        lhs = model.getLhs(constr)

        # retrieve constraint bound for single inequity
        # for example if constraint is 'x >= 10' then lhs = 10, rhs = 1e20, so constraint bound is 10
        # for constraint 'x <= 10' lhs = -1e20, rhs = 1e20 and constraint bound is 10
        bound = min(abs(rhs), abs(lhs))

        double_inequity = (lhs != rhs) and (lhs > -1e20) and (rhs < 1e20)

        new_constr = Expr()

        for var_name in vars_in_constr_map.keys():
            var_index = clauses.var_index_dict[var_name]

            # 1) if var index is in assumptions then we need to decrease bound on var coefficient and
            # don't add it to the new constraint
            # 2) if -var index is in assumptions then this var is equals to 0 and we just don't need to add it
            # to the new constraint
            # 3) else we need to add this var with corresponding coefficient
            if var_index in assumptions:
                if not double_inequity:
                    bound -= vars_in_constr_map[var_name]
                else:
                    rhs -= vars_in_constr_map[var_name]
                    lhs -= vars_in_constr_map[var_name]
            elif -var_index not in assumptions:
                assert model.getVars()[var_index - 1].name == clauses.model.getVars()[var_index - 1].name
                new_constr += model.getVars()[var_index - 1] * vars_in_constr_map[var_name]

        if lhs != rhs:
            if double_inequity:
                model.addCons((rhs >= new_constr) >= lhs)
            else:
                add_single_inequality(lhs=lhs, rhs=rhs, bound=bound, new_constr=new_constr, model=model)
        else:
            model.addCons(new_constr == bound)

        model.delCons(constr)

    model.optimize()

    if model.getStatus() == "optimal":
        return True, {'time': model.getSolvingTime()}, model.getSolVal(model.getBestSol(), model.getObjective())
    elif model.getStatus() == "infeasible":
        return False, {'time': model.getSolvingTime()}, None


if __name__ == '__main__':
    backdoor = initialize_backdoor()
    instance_format, file = parse_arguments()
    model = initialize_model(instance_format, file)

    time_to_solve = {}
    start_time = datetime.now()
    obj_value = float('inf')

    for i in range(2 ** len(backdoor)):
        print(i)
        assumptions = backdoor.copy()

        for j in range(len(assumptions)):
            if i & 2 ** j != 0:
                assumptions[j] = -assumptions[j]

        status, _ = Scip().propagate(clauses=ScipILPClause(model), assumptions=assumptions)

        if status:
            sol_status, stats, current_obj = solve_with_variable_substitution(clauses=ScipILPClauseForValidation(model),
                                                                              assumptions=assumptions)

            time_to_solve[stats['time']] = assumptions

            if sol_status:
                obj_value = min(obj_value, current_obj)

    with open('../solving_statistics', 'w') as solving_stats:
        solving_stats.write("len: " + str(len(time_to_solve)) + "\n")
        solving_stats.write(str(time_to_solve))

    print("Total time: ", datetime.now() - start_time)
    print("Objective: ", obj_value)
