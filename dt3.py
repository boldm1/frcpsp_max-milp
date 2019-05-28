
#dt3 mip model from Naber & Kolisch (2014)

from gurobipy import *

import os

def mip_solve(project):    

    model = Model("Intensity-based (FB-DT3)")

    #Index sets
    V = [task.id for task in list(project.tasks.values())] # list of task indices
    n = V[-2] # index of final non-dummy activity
    N = V[1:-1] # list of non-dummy task indices
    R = list(range(len(project.R_max))) # list of resource indices
    T = list(range(0,200)) # planning horizon
    T_act = [list(range(project.tasks[j].ES, project.tasks[j].LF+1)) for j in V] # list containing lists of feasible processing periods for each activity
    ST_act = [list(range(project.tasks[j].ES, project.tasks[j].LS+1)) for j in V] # list containing lists of feasible starting periods for each activity
    FT_act = [list(range(project.tasks[j].EF, project.tasks[j].LF+1)) for j in V] # list containing lists of feasible finishing periods for each activity

    #Variables
    x = model.addVars([(j,t) for j in N for t in T_act[j]], name = "x", vtype = GRB.BINARY)
    y = model.addVars([(j,t) for j in N for t in T_act[j]], name = "y", vtype = GRB.BINARY)
    delta = model.addVars([(r,j,t) for r in R for j in N for t in T_act[j]+[project.tasks[j].LF+1]], name = "delta", vtype = GRB.BINARY)
    q = model.addVars([(r,j,t) for r in R for j in N for t in T_act[j]+[project.tasks[j].ES-1,project.tasks[j].LF+1]], name = "q", vtype = GRB.CONTINUOUS)
    v = model.addVars([(j,t) for j in N for t in T_act[j]+[project.tasks[j].LF+1]], name = "v", vtype = GRB.CONTINUOUS)
    C_max = model.addVar(name = "C_max", vtype = GRB.CONTINUOUS)

    #Objective
    model.setObjective(C_max, GRB.MINIMIZE)

    #Constraints
    #model.addconstr(C_max >= T_min, name = "(13)") # not strictly necessary
    model.addConstrs((C_max >= project.tasks[j].LF - quicksum(y[j,t] for t in T_act[j]) + 1 for j in N), name = "(31)")
    model.addConstrs((q[r,j,t] <= project.tasks[j].q_max[r]*x[j,t] for r in R for j in N for t in ST_act[j] if t not in FT_act[j]), name = "(42a)")
    model.addConstrs((q[r,j,t] <= project.tasks[j].q_max[r]*(x[j,t] - y[j,t]) for r in R for j in N for t in ST_act[j] if t in FT_act[j]), name = "(42b)")
    model.addConstrs((q[r,j,t] <= project.tasks[j].q_max[r]*(1 - y[j,t]) for r in R for j in N for t in FT_act[j] if t not in ST_act[j]), name = "(42c)")
    model.addConstrs((q[r,j,t] >= project.tasks[j].q_min[r]*x[j,t] for r in R for j in N for t in ST_act[j] if t not in FT_act[j]), name = "(43a)")
    model.addConstrs((q[r,j,t] >= project.tasks[j].q_min[r]*(x[j,t] - y[j,t]) for r in R for j in N for t in ST_act[j] if t in FT_act[j]), name = "(43b)")
    model.addConstrs((q[r,j,t] >= project.tasks[j].q_min[r]*(1 - y[j,t]) for r in R for j in N for t in FT_act[j] if t not in ST_act[j]), name = "(43c)")
    model.addConstrs((q[r,j,t] >= project.tasks[j].alpha[r]*q[project.tasks[j].k,j,t] + project.tasks[j].beta[r]*(x[j,t] - y[j,t]) for j in N for r in project.tasks[j].r_dep for t in T_act[j]), name = "(44)")
    model.addConstrs((q[project.tasks[j].k,j,t] >= project.tasks[j].w[project.tasks[j].k]*(v[j,t+1] - v[j,t]) for j in N for t in T_act[j]), name = "(45)")
    model.addConstrs((quicksum(q[r,j,t] for t in T_act[j]) >= project.tasks[j].w[r] for r in R for j in N if r != project.tasks[j].k), name = "(46)")
    model.addConstrs((quicksum(q[r,j,t] for j in N if t in T_act[j]) <= project.R_max[r] for r in R for t in T), name = "(5)")
    model.addConstrs((quicksum(delta[r,j,tau] for tau in range(t,t+project.l_min)) <= 1 for r in R for j in N for t in range(project.tasks[j].ES,project.tasks[j].LF-project.l_min+3) if project.l_min >= 2), name = "(6)")
    model.addConstrs((q[r,j,t] - q[r,j,t-1] <= project.tasks[j].q_max[r]*delta[r,j,t] for r in R for j in N for t in T_act[j]+[project.tasks[j].LF+1]), name = "(7)")
    model.addConstrs((q[r,j,t-1] - q[r,j,t] <= project.tasks[j].q_max[r]*delta[r,j,t] for r in R for j in N for t in T_act[j]+[project.tasks[j].LF+1]), name = "(8)")
    model.addConstrs((q[r,j,project.tasks[j].ES-1] == 0 for r in R for j in N), name = "(9a)")
    model.addConstrs((q[r,j,project.tasks[j].LF+1] == 0 for r in R for j in N), name = "(9b)")
    model.addConstrs((v[j,t] <= x[j,t] for j in N for t in ST_act[j]), name = "(32)")
    model.addConstrs((v[j,t] >= y[j,t] for j in N for t in FT_act[j]), name = "(33)")
    model.addConstrs((x[SS[0],t+SS[1]] <= x[j,t] for j in N for SS in project.tasks[j].successors[0] if SS[0] != n+1 for t in ST_act[j] if t+SS[1] in ST_act[SS[0]]), name = "(34a)")
    model.addConstrs((y[SF[0],t+SF[1]] <= x[j,t] for j in N for SF in project.tasks[j].successors[1] if SF[0] != n+1 for t in ST_act[j] if t+SF[1] in FT_act[SF[0]]), name = "(34b)")
    model.addConstrs((x[FS[0],t+FS[1]] <= y[j,t] for j in N for FS in project.tasks[j].successors[2] if FS[0] != n+1 for t in FT_act[j] if t+FS[1] in ST_act[FS[0]]), name = "(34c)")
    model.addConstrs((y[FF[0],t+FF[1]] <= y[j,t] for j in N for FF in project.tasks[j].successors[3] if FF[0] != n+1 for t in FT_act[j] if t+FF[1] in FT_act[FF[0]]), name = "(34d)")
    model.addConstrs((v[j,t] <= v[j,t+1] for j in N for t in T_act[j]), name = "(35)")
    model.addConstrs((x[j,t-1] <= x[j,t] for j in N for t in T_act[j] if t != project.tasks[j].ES), name = "(36)")
    model.addConstrs((y[j,t-1] <= y[j,t] for j in N for t in T_act[j] if t != project.tasks[j].ES), name = "(37)")
    model.addConstrs((v[j,project.tasks[j].ES] == 0 for j in N), name = "(38b)")
#    model.addConstrs((v[j,project.tasks[j].LF] == 1 for j in N), name = "(39)")
    model.addConstrs((v[j,project.tasks[j].LF+1] == 1 for j in N), name = "(39)")
    model.addConstrs((x[j,t] == 1 for j in N for t in range(project.tasks[j].LS, project.tasks[j].LF+1)), name = "(40)")
    model.addConstrs((y[j,t] == 0 for j in N for t in range(project.tasks[j].ES, project.tasks[j].EF)), name = "(41)")
    model.addConstrs((q[r,j,t] >= 0 for r in R for j in N for t in T_act[j]+[project.tasks[j].ES-1,project.tasks[j].LF+1]), name = "(10)")
    model.addConstrs((0 <= v[j,t] <= 1 for j in N for t in T_act[j]+[project.tasks[j].LF+1]), name = "(47)")

    model.optimize()
    status = model.status
    current_dir = os.path.dirname(__file__)
    if status == GRB.Status.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
        exit(0)
    elif status == GRB.Status.OPTIMAL:
        print('The optimal objective value is %g' %model.objVal)
        # write model to file
        model.write(os.path.join(current_dir, 'solutions', '%s.lp' %project.name))
        # write solution to file
        model.write(os.path.join(current_dir, 'solutions', '%s.sol' %project.name))
        exit(0)
    elif status == GRB.Status.INFEASIBLE:
        model.computeIIS()
        model.write(os.path.join(current_dir, 'solutions', '%s.ilp' %project.name))
        print("The model cannot be solved because it is infeasible. IIS written to file '%s.ilp'" %project.name)
        exit(0)
    


    
    



