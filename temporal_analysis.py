from numpy import *
from copy import deepcopy

# updates dgraph for a given project
def temporal_analysis(project):
    dgraph = deepcopy(project.dgraph)
    ### floyd-warshall algorithm ###
    for k in project.tasks:
        for i in project.tasks:
            jrange = range(i-(len(project.tasks)-1),i+1)
            for j in [j%len(project.tasks) for j in jrange]:
                dgraph[i][j][0][0] = max(dgraph[i][j][0][0], max(dgraph[i][k][0][0]+dgraph[k][j][0][0], dgraph[i][k][0][1]+dgraph[k][j][1][0])) # min(d_si->sj, d_si->k + d_k->sj)
                dgraph[i][j][0][1] = max(dgraph[i][j][0][1], max(dgraph[i][k][0][0]+dgraph[k][j][0][1], dgraph[i][k][0][1]+dgraph[k][j][1][1])) # min(d_si->fj, d_si->k + d_k->fj)
                dgraph[i][j][1][0] = max(dgraph[i][j][1][0], max(dgraph[i][k][1][0]+dgraph[k][j][0][0], dgraph[i][k][1][1]+dgraph[k][j][1][0])) # min(d_fi->sj, d_fi->k + d_k->sj)
                dgraph[i][j][1][1] = max(dgraph[i][j][1][1], max(dgraph[i][k][1][0]+dgraph[k][j][0][1], dgraph[i][k][1][1]+dgraph[k][j][1][1])) # min(d_fi->fj, d_fi->k + d_k->fj)
    ### checking feasibility ###
    for i in project.tasks:
        if dgraph[i][i][0][0] != 0 or dgraph[i][i][1][1] != 0:
            print('Project is infeasible.')
            return(1)
    project.dgraph = deepcopy(dgraph)
    ### update d_min, d_max, ES, LS, q_min, q_max ###
    for task in project.tasks.values():
        task.d_min = int(dgraph[task.id][task.id][0][1])
        task.d_max = int(-dgraph[task.id][task.id][1][0])
        task.ES = int(dgraph[0][task.id][0][0])
        task.LS = int(-dgraph[task.id][0][0][0])
        task.EF = task.ES + task.d_min
        task.LF = task.LS + task.d_max
        # only updating work-content resource limits
        if task.d_max == 0:
            task.q_min[0] = 0
            task.q_max[0] = 0
        else:
            task.q_min[0] = task.w_k/task.d_max
            task.q_max[0] = task.w_k/task.d_min



