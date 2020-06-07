"""
Simulation implementation module.
=================================

Contains the definitions of the different concrete implementations
of the Simulation base class.

NOTE: all of the class belows are
composed by using the `with_` decorators from
sim.core.sim_0.
They may seem empty at first, but the decorators
perform the actual extension at the class level

"""

import numpy as np
from random import choices

from sim.core.sim_0 import *


# * Proposer selection implementations

# ** Log
def log_proposer_selection(self):
    """Implementation of the logarithmic proposer selection function.
    Note that the base of the log is irrelavant since the vector
    of logs will be normalized.

    Uses random.choices with weights vector determined
    by log(1 + x).

    Returns a single node as result.

    """

    # TODO make it np.log(1 + np.array([...]))
    probs=np.array([np.log(1 + n.v(self.s)) for n in self.nodes])
    return choices(self.nodes,probs,k=1)[0]

# ** Rand

def random_proposer_selection(self):
    """ Overrides selection procedure to sample nodes
    randomly with eqaul probability """
    # probs = [1/self.m for _ in range(self.m)]
    return choices(self.nodes,k=1)[0] # equiprobablt is the default




# * Random scheme

# ** Random selection, const reward

@with_selection_fn(random_proposer_selection)
class RandomSim(Simulation):
    """RadomSim extends the normal simulation with random proposer selection.
    Used for control/refernce condition
    """
    pass


# * Constant schemes

# ** Linear selection, const reward
class ConstSim(Simulation):
    """Constant reward, linear selection simulation.
    Just a placeholder, this is simply the default for Simulation

    """
    pass

# ** log selection, const reward

@with_selection_fn(log_proposer_selection)
class LogConstSim(Simulation):
    """LogConstSim extends basic simulation with log based proposer
    selection.
    """
    pass


# * Geometric schemes

# define geometric reward function:

def r_g(params):
    """Geometric reward function.

    accepts a dictionary specifying required
    parameters, and 't'.

    Suitable params dictionary is obtained by invoking .params() on a
    simulaion instance

    (1+R)^(t/T) - (1+R)^((t-1)/T)

    """
    return (1+params['R'])**(params['t']/params['T'])\
                    - (1+params['R'])**((params['t']-1)/params['T'])

# ** Linear selection, Geom reward

@with_reward_fn(r_g)
class GeomSim(Simulation):
    """GeomSim extend base Simulation with geometric reward function."""
    pass


# ** Log selection, Geom reward

@with_selection_fn(log_proposer_selection)
@with_reward_fn(r_g)
class LogGeomSim(Simulation):
    """LogGeomSim extend base Simulation with geometric reward function,
    and log10 based proposer selection.

    """
    pass
