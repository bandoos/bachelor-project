"""
Implementation of the geometric reward based
simulaion classes.

Includes both `geom` (GeomSim) and `log_geom` (LogConstSim)

"""

import numpy as np
from random import choices

from sim.core.sim_0 import *

def r_g(params):
    """Geometric reward function.

    accepts a dictionary specifying required
    parameters, and 't'.

    Suitable params dictionary is obtained by invoking
    .params() on a simulaion instance

    (1+R)^(t/T) - (1+R)^((t-1)/T)

    """
    return (1+params['R'])**(params['t']/params['T'])\
                    - (1+params['R'])**((params['t']-1)/params['T'])

@with_reward_fn(r_g)
class GeomSim(Simulation):
    """GeomSim extend base Simulation with geometric reward function."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #self.r = r_g

@with_reward_fn(r_g)
class LogGeomSim(Simulation):
    """LogGeomSim extend base Simulation with geometric reward function,
    and log10 based proposer selection.
    """

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        #self.r = r_g

    def select_proposer(self):
        probs=np.array([np.log(1+n.v(self.s)) for n in self.nodes])
        chosen = choices(self.nodes,probs,k=1)[0]
        return chosen


# def add_method(name,fn):
#     def d(c):
#         setattr(c,name,fn)
#         return c
#     return d


# @add_method('mona',lambda self,x: "mona"+x)
# class A ():
#     pass

# a = A()
# a.mona
# a.mona('ti')


# @add_method('mona',10)
# class B ():
#     pass

# b = B()
