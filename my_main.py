from pyscipopt.scip import Model, Row, Expr

old = Model()

x = old.addVar(vtype='B', name='X')
y = old.addVar(vtype='B', name='Y')

old.addCons(x + y >= 1)
old.addCons(x == 0)

model = Model(sourceModel=old, threadsafe=True)

to_delete = []

assumptions = [-2]
var_index_dict = {'X': 1, 'Y': 2}

for constr in model.getConss():
    vars_in_constr_map = model.getValsLinear(constr)

    rhs = model.getRhs(constr)
    lhs = model.getLhs(constr)

    bound = min(abs(rhs), abs(lhs))
    new_constr = Expr()

    for var_name in vars_in_constr_map.keys():
        var_index = var_index_dict[var_name]

        if var_index in assumptions:
            bound -= vars_in_constr_map[var_name]
        elif -var_index not in assumptions:
            # assert model.getVars()[var_index - 1].name == clauses.model.getVars()[var_index - 1].name
            new_constr += model.getVars()[var_index - 1] * vars_in_constr_map[var_name]

    if rhs > lhs:
        model.addCons(new_constr >= bound)
    elif lhs > rhs:
        model.addCons(new_constr <= bound)
    else:
        model.addCons(new_constr == bound)

    to_delete.append(constr)

for c in to_delete:
    model.delCons(c)

# old_cons = model.getConss()
#
# new_vars = model.getVars()
# new_x = new_vars[0]
# new_y = new_vars[1]
#
# c1 = Expr()
# c1 += new_x * 1.0
# model.addCons(c1 >= 1.0)
# model.delCons(old_cons[0])
#
# c2 = Expr()
# c2 += new_x * 1.0
# model.addCons(c2 == 0.0)
# model.delCons(old_cons[1])

model.presolve()

print("SOLS: ", len(model.getSols()))
print("STAT: ", model.getStatus())
