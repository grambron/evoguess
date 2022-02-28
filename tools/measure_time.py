from gurobipy import read, Model
from gurobipy.gurobipy import GRB

model = Model('copy')

x = model.addVar(name="X", vtype=GRB.INTEGER)
y = model.addVar(name="Y", vtype=GRB.INTEGER)
z = model.addVar(name="Z", vtype=GRB.INTEGER)

model.addConstr(-x + 5 * y + 1 == 5 * z)
model.addConstr(2 * x + 3 * y <= 10)


model.update()

# что дороже - копировать модель или удалять констрейнты?
# for constr in model.getConstrs():
#     row = model.getRow(constr)
#     rhs = constr.rhs
#     model.remove(constr)

model.optimize()

print(model.status)

print("======")
for var in model.getVars():
    print(f'{var.VarName} = {var.X}')
