from pyscipopt.scip import Model, Row, Expr

model = Model()

x = model.addVar(vtype='B', name='X')
y = model.addVar(vtype='B', name='Y')

model.addCons(x + y <= 1)

model2 = Model(sourceModel=model, threadsafe=True, origcopy=True)

total_cons = model2.getConss()
assert len(total_cons) == 1

constraint = total_cons[0]

new_y = model.getVars()[1]
assert new_y.name == 'Y'

new_constraint = Expr()
new_constraint += new_y * 1

model2.addCons(new_constraint <= 1)
model2.delCons(constraint)

model2.optimize()
