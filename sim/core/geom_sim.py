import numpy as np
from random import choices

from sim.core.sim_0 import *

#r_g =  lambda n:
def r_g(n):
    """Geometric reward function.
    (1+R)^(t/T) - (1+R)^((t-1)/T)
    """
    return (1+n['R'])**(n['t']/n['T'])\
                    - (1+n['R'])**((n['t']-1)/n['T'])


class GeomSim(Simulation):
    """GeomSim extend base Simulation with geometric reward function
    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.r = r_g


k = 20
di = 3
class LogGeomSim(Simulation):
    """LogGeomSim extend base Simulation with geometric reward function,
    and log10 based proposer selection.
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.r = r_g

    def select_proposer(self):
        probs=np.array([np.log(1+k*n.v(self.s))/3 for n in self.nodes])
        chosen = choices(self.nodes,probs,k=1)[0]
        return chosen
