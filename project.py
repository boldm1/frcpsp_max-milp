
from numpy import *

from temporal_analysis import temporal_analysis

class Project():

    def __init__(self, name, tasks, R_max, l_min):         
        self.name = name
        self.tasks = tasks # tasks = {task_id : task_object}
        self.R_max = R_max # resource availabilities
        self.l_min = l_min # min. block length
        self.T = 40 
        self.init_dgraph = self.dgraph_init() # initial dgraph. Useful for unscheduling step
        self.dgraph = self.dgraph_init()
        temporal_analysis(self)

    def dgraph_init(self):
        dgraph = [[array([[-self.T,-self.T], [-self.T,-self.T]]) for j in self.tasks] for i in self.tasks] # dgraph[i][j] = [[d_si->sj, d_si->fj],[d_fi->sj, d_fi->fj]]
        for i in self.tasks:
            dgraph[i][i] = array([[0,self.tasks[i].d_min],[-self.tasks[i].d_max,0]])
        for i in self.tasks:
            for j in range(4): # precedence relation type
                for k in self.tasks[i].successors[j]:
                    if j == 0: #S->S relation
                        dgraph[i][k[0]][0][0] = k[1]
                    if j == 1: #S->F relation
                        dgraph[i][k[0]][0][1] = k[1]
                    if j == 2: #F->S relation
                        dgraph[i][k[0]][1][0] = k[1]
                    if j == 3: #F->F relation
                        dgraph[i][k[0]][1][1] = k[1]
        return(dgraph)    
