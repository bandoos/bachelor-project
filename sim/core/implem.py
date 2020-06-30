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

from sim.core.sel_f import \
    random_proposer_selection, \
    linear_proposer_selection, \
    log_proposer_selection

from sim.core.rew_f import \
    r_const,\
    r_g


# * Random scheme

# ** Random selection based

# *** with const rew
@with_reward_fn(r_const)
@with_selection_fn(random_proposer_selection)
class RandomSim(Simulation):
    """RadomSim extends the normal simulation with random proposer selection.
    Used for control/refernce condition
    """
    pass

# *** with geom rew
@with_reward_fn(r_g)
@with_selection_fn(random_proposer_selection)
class RandomGeomSim(Simulation):
    """RadomSim extends the normal simulation with random proposer selection.
    Used for control/refernce condition
    """
    pass


# * Constant schemes

# ** Linear selection, const reward
@with_reward_fn(r_const)
@with_selection_fn(linear_proposer_selection)
class ConstSim(Simulation):
    """Constant reward, linear selection simulation.
    Just a placeholder, this is simply the default for Simulation

    """
    pass

# ** log selection, const reward
@with_reward_fn(r_const)
@with_selection_fn(log_proposer_selection)
class LogConstSim(Simulation):
    """LogConstSim extends basic simulation with log based proposer
    selection.
    """
    pass


# * Geometric schemes

# ** Linear selection, Geom reward
@with_reward_fn(r_g)
@with_selection_fn(linear_proposer_selection)
class GeomSim(Simulation):
    """GeomSim extend base Simulation with geometric reward function."""
    pass


# ** Log selection, Geom reward
@with_reward_fn(r_g)
@with_selection_fn(log_proposer_selection)
class LogGeomSim(Simulation):
    """LogGeomSim extend base Simulation with geometric reward function,
    and log10 based proposer selection.

    """
    pass
