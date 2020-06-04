import numpy as np
from random import choices

from sim.core.sim_0 import *

k = 20
di = 3
class LogConstSim(Simulation):
    """LogConstSim extends basic simulation with log10 based proposer
    selection.
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def select_proposer(self):
        probs=np.array([np.log(1+k*n.v(self.s))/di for n in self.nodes])
        chosen = choices(self.nodes,probs,k=1)[0]
        return chosen
