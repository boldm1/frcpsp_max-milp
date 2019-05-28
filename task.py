import math

class Task():
    
    def __init__(self, id, successors, k, w_k, q_min, q_max):
        self.id = id
        self.successors = successors # e.g. successor[i=2(FS)] = [(FS successor id, min. time-lag),...]
        self.q_min = q_min
        self.q_max = q_max
        try:
            self.d_max = math.ceil(w_k/self.q_min[k])
            self.d_min = math.ceil(w_k/self.q_max[k])
        except ZeroDivisionError:
            self.d_max = 0
            self.d_min = 0
        self.w_k = w_k # principle work-content
        self.k = k # index of principle resource 
        self.r_dep = [i for i,v in enumerate(q_min) if q_min[i] < q_min[i] if i != self.k] # dependent resources
        self.r_ind = [i for i,v in enumerate(q_min) if q_min[i] == q_min[i] if i != self.k] # independent resources
        ### q_rjt = alpha_krj*q_krj + beta_krj ###
        self.alpha = [(q_max[r]-q_min[r])/(q_max[k]-q_min[k]) for r in self.r_dep]
        self.beta = [q_min[r]-q_min[k]*self.alpha[r] for r in self.r_dep]
        ### list of work-contents ###
        self.w = []
        for r in range(len(q_min)):
            if r == k:
                self.w.append(w_k)
            elif r in self.r_dep:
                self.w.append(self.alpha[r]*w_k + self.beta[r])
            elif r in self.r_ind:
                self.w.append(q_min[r]*self.d_min)
        self.ES = float('-inf') # Earliest start wrt temporal constraints (updated in temporal_analysis function)
        self.LS = float('inf')
        self.EF = float('-inf')
        self.LF = float('inf')

