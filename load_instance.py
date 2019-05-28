import sys
import re
import os
from pathlib import Path

from task import Task
from project import Project
from schedule import Schedule
from temporal_analysis import temporal_analysis
from dt3 import mip_solve

def load_instance(path_to_file):
    f = open(path_to_file, 'r')
    raw_lines = f.read().splitlines()
    stripped_lines = []
    for line in raw_lines:
        line = line.replace('\t', ',').replace('[', '').replace(']', '')
        stripped_lines.append(re.split(',', line))
    first_line = stripped_lines[0]
    n_activities = int(first_line[0]) # number of activities (incl. dummy activities)
    n_resources = int(first_line[1])
    ### loading tasks ###
    tasks = {}
    for activity in range(n_activities):
        ### first block ###
        line1 = stripped_lines[activity+1]
        task_id = int(line1[0])
        n_successors = [int(line1[2]), int(line1[3]), int(line1[4]), int(line1[5])] # [# SS successors, # SF successors, # FS successors, # FF successors]
        successors = [[] for i in range(4)]
        k = 0 # counter to track where in line1 to get desired info.
        for i in range(4):
            if n_successors[i] > 0:
                try:
                    for j in range(n_successors[i]):
                        successors[i].append((int(line1[6+2*k+j]), int(line1[6+2*k+n_successors[i]+j]))) # e.g. successor[i=2(FS)] = [(FS successor id, min. time-lag),...]
                except IndexError:
                    if i == 0:
                        print('Was expecting a start -> start successor for activity %d, but none found.' %task_id)
                    elif i == 1:
                        print('Was expecting a start -> finish successor for activity %d, but none found.' %task_id)
                    elif i == 2:
                        print('Was expecting a finish -> start successor for activity %d, but none found.' %task_id)
                    elif i == 3:
                        print('Was expecting a finish -> finish successor for activity %d, but none found.' %task_id)
                    sys.exit(1)
            k += n_successors[i]
        ### second block ###
        line2 = stripped_lines[n_activities+activity+1]
        k = int(line2[2]) # principle resource index
        w_k = int(line2[3]) # principle resource work-content
        q_min = [] # min. per-period resource allocation for each resource 
        q_max = [] # max. per-period resource allocation for each resource
        for r in range(n_resources):
            q_min.append(int(line2[4+2*r]))
            q_max.append(int(line2[4+2*r+1]))
        task = Task(task_id, successors, k, w_k, q_min, q_max)
        tasks[task_id] = task 
    last_line = stripped_lines[2*n_activities+1]
    R_max = [] # resource_availabilities
    for r in range(n_resources):
        R_max.append(int(last_line[r]))
    l_min = int(last_line[n_resources]) # min. block length
    name = os.path.splitext(os.path.basename(os.path.normpath(path_to_file)))[0]
    project = Project(name, tasks, R_max, l_min)
    return(project)


test_instances_dir = Path("test_instances")
#project = load_instance(test_instances_dir/'test_instance3.sch')
project = load_instance(test_instances_dir/'sm_j10'/'PSP3_r1.sch')
#print(project.R_max)
temporal_analysis(project)
#for task in project.tasks.values():
#   print('(task.ES,task.LS): (%d,%d)' %(task.ES,task.LS))
#    print('(task.d_min,task.d_max): (%d,%d)' %(task.d_min,task.d_max))
#    print('(task.q_min,task.q_max): (%.2f,%.2f)' %(task.q_min[0],task.q_max[0]))

mip_solve(project)



