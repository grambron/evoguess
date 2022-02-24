from pyscipopt.scip import Model, Row, Expr

model = Model()

x = model.addVar(vtype='B', name='X')
y = model.addVar(vtype='B', name='Y')

model.addCons(x + y <= 1)

model2 = Model(sourceModel=model, threadsafe=True, origcopy=True)

total_cons = model2.getConss()
if len(total_cons) != 1:
    raise Exception("size")

constraint = total_cons[0]

new_y = model.getVars()[1]
new_constraint = Expr()
new_constraint += new_y * 2

x2 = model2.addVar(vtype='B', name='X1')

model2.addCons(x2 <= 1)
model2.delCons(constraint)

print(len(model2.getConss()))

model2.optimize()
