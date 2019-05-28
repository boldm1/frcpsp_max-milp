class Schedule():
    def __init__(self, project):
        self.tasks_scheduled = []
        self.task_starts = {}
        self.task_ends = {}
        self.task_resource_usage = [[[0 for t in range(project.T)] for i in project.tasks] for r in range(len(project.R_max))]
        self.resource_availability = [[project.R_max[r] for t in range(project.T)] for r in range(len(project.R_max))]
            
