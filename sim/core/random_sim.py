"""
Random simulation module

"""
from random import choices

from sim.core.sim_0 import *

class RandomSim(Simulation):
    """RadomSim extends the normal simulation with random proposer selection.
    Used for control/refernce condition
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.probs = [1/self.m for _ in range(self.m)]

    def select_proposer(self):
        """ Overrides selection procedure to sample nodes
        randomly with eqaul probability """
        return choices(self.nodes,self.probs,k=1)[0]
