from random import choices

from sim.core.sim_0 import *

class RandomSim(Simulation):
    """RadomSim extends the normal simulation with random proposer selection.
    Used for control/refernce condition
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    def select_proposer(self):
        probs=[1/self.m for _ in range(self.m)]
        chosen = choices(self.nodes,probs,k=1)[0]
        return chosen
