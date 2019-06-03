
from pathlib import Path

from load_instance import load_instance
from schedule import Schedule
from temporal_analysis import temporal_analysis
from dt3 import mip_solve

test_instances_dir = Path("test_instances")
#project = load_instance(test_instances_dir/'sm_j30'/'PSP233_r1.sch')
project = load_instance(test_instances_dir/'testset_ubo20'/'psp74_r1.sch')
#project = load_instance(test_instances_dir/'testset_ubo100'/'psp11_r5.sch')
#project = load_instance(test_instances_dir/'testset_ubo100'/'psp11_r5.sch')
#print(project.R_max)
temporal_analysis(project)
#for task in project.tasks.values():
#   print('(task.ES,task.LS): (%d,%d)' %(task.ES,task.LS))
#    print('(task.d_min,task.d_max): (%d,%d)' %(task.d_min,task.d_max))
#    print('(task.q_min,task.q_max): (%.2f,%.2f)' %(task.q_min[0],task.q_max[0]))

mip_solve(project)
