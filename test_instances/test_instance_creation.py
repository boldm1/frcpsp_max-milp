
# given a folder of frcpsp problem instances, converts all instances to frcpsp/max problem instances.

import os
import re
import math
import random
from shutil import copyfile

def convert_instances(path_to_rcpspmax_folder):
    os.chdir(path_to_rcpspmax_folder)
    for full_filename in os.listdir(path_to_rcpspmax_folder):
        if os.path.splitext(full_filename)[1] == '.SCH':
            filename = os.path.splitext(full_filename)[0]
            f = open(full_filename, 'r')
            raw_lines = f.read().splitlines()
            first_line = re.split('\t', raw_lines[0])
            n_activities = int(first_line[0])+2
            n_resources = int(first_line[1])
            for r in range(n_resources):
                f = open(filename + '_r%d.sch' %(r+1), 'w+')
                r_activities = [] # activities that require resource r
                for activity in range(n_activities):
                    line1 = re.split('\t', raw_lines[activity+1])
                    line2 = re.split('\t', raw_lines[n_activities+activity+1])
                    d_hat = int(line2[2])
                    q_hat_prime = int(line2[3+r]) # work-content resource usage
                    if (activity == 0) or (activity == n_activities-1) or (q_hat_prime != 0):
                        r_activities.append(activity)
                first_line = raw_lines[0].replace('\t', ',')
                first_line = re.split(',', first_line)
                first_line[0] = '%d' %len(r_activities)
                first_line.append('\n')
                new_raw_first_line = '\t'.join(first_line)
                f.write(new_raw_first_line)
                for activity in r_activities:
                    ### Getting new line1 ###
                    line1 = raw_lines[activity+1].replace('\t', ',')
                    line1 = re.split(',', line1)
                    n_successors = int(line1[2]) #number of S->S successors
                    to_remove = []
                    for j in range(n_successors):
                        successor = int(line1[3+j])
                        if successor not in r_activities:
                            to_remove.append(j)
                        else:
                            line1[3+j] = '%d' %r_activities.index(successor)
                    line1[0] = '%d' %r_activities.index(activity)
                    line1[2] = str(n_successors - len(to_remove))
                    for j in to_remove[::-1]: # reverse list to avoid messing up indices
                        del line1[3+n_successors+j]
                    for j in to_remove[::-1]:
                        del line1[3+j]
                    line1[3:3] = ['0', '0', '0'] # number of S->F, F->S, F->F successors
                    line1.append('\n')
                    new_raw_line1 = '\t'.join(line1)
                    f.write(new_raw_line1)
                for activity in r_activities:
                    ### Getting new line2 ###
                    line2 = raw_lines[n_activities+activity+1].replace('\t', ',')
                    line2 = re.split(',', line2)
                    d_hat = int(line2[2])
                    q_hat = [] # resource requirements (work-content resource comes first)
                    q_hat.append(int(line2[3+r]))
                    for r_prime in range(n_resources):
                        q_hat.append(int(line2[3+r_prime]))
                    del q_hat[r+1] # remove repeated work-content resource requirement
                    w = d_hat*q_hat[0]
                    q_min, q_max = [], []
                    for i in range(len(q_hat)):
                        q_min.append(random.randint(math.ceil(q_hat[i]/2), q_hat[i]))
                        q_max.append(random.randint(q_hat[i], 2*q_hat[i]))
                    line2[2] = '0'
                    line2[3] = '%d' %w
                    line2 = line2[0:4]
                    for r_prime in range(n_resources):
                        line2.append('%d' %q_min[r_prime])
                        line2.append('%d' %q_max[r_prime])
                    line2.append('\n')
                    new_raw_line2 = '\t'.join(line2)
                    f.write(new_raw_line2)
                ### last line ###
                last_line = raw_lines[2*n_activities+1].replace('\t', ',')
                last_line = re.split(',', last_line)
                last_line.insert(0, last_line[r])
                del last_line[r+1] # remove repeated work-content resource availability
                l = random.choice([2,3,4]) # min. block length
                last_line.append('%d' %l)
                new_raw_last_line = '\t'.join(last_line)
                f.write(new_raw_last_line)
            os.remove(full_filename) # delete rcpsp/max version of the file

convert_instances('/home/boldm1/Documents/phd/frcpsp/frcpsp_max/test_instances/sm_j10')

