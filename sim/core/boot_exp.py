"""
experiment bootstrap module
===========================

defines the experiment function `boot_exp`
and the stats aggregator `EpisodeStats`.
"""
import numpy as np
import math
import sys

from time import time
from functools import *

#from sim.core.sim_0 import Simulation
from sim.core.decorators import *

from sim.core.stake_f import stake_f_label_to_fn
#from sim.core.sim_0 import Simulation

from sim.core.implem import \
    ConstSim, LogConstSim, \
    GeomSim,  LogGeomSim, \
    RandomSim

sim_label_to_class ={
    'random':  RandomSim,
    'const':   ConstSim,
    'log_const': LogConstSim,
    'geom': GeomSim,
    'log_geom': LogGeomSim,
}

def gini_coeff(pop):
    """ Computes Gini coefficient for a sample """
    mu = np.mean(pop)
    n2 = len(pop)**2
    diffsum = sum([abs(x - y) for x in pop for y in pop])
    return diffsum/(2*n2*mu)

class EpisodeStats():
    """Stateful aggregator for experiment response variables.

    `self.set_init` should be called berfore each simulation run,
    passing the sim instance.

    `self.set_finals` should be called after a simulation terminated
    passing the sim instance to finalize the statistics.

    `self.mk_row` should be called after set_finals with no arguments
    and will format as csv row string the current state

    """

    indep_keys = ["m","T","c","R","sim","stake_f"]
    response_keys = ["var_0","var_T",
                     "gini_0","gini_T",
                     "under_target","avg_loss",
                     "over_target","avg_gain"]

    header = ",".join ([*indep_keys,*response_keys]) + "\n"

    def __init__(self,params):
        """Creates the aggregator given simulation parameters"""
        self.prefix = ",".join ([str (params [k])
                                 for k in EpisodeStats.indep_keys]) + ","

    def set_init(self,sim):
        """To be called before each sulation repetition."""
        init_vs = [n.stake for n in sim.nodes] # initial stakes are already fractional
        self.gini_0 = gini_coeff(init_vs) # save initial state of stats
        self.var_0 = np.var(init_vs)

    def set_finals(self,sim):
        """To be called after each simulation repetition."""
        final_vs = [d.v(sim.s) for d in sim.nodes] # get final fractional stakes

        self.gini_T= gini_coeff(final_vs) # compute final stats
        self.var_T = np.var(final_vs)

        # ** Under/over target analysis
        under = [n for n in sim.nodes # who was penalized by the process
                 if n.v(sim.s) < n.stake_0]
        over = [n for n in sim.nodes # who was favored by the process
                if n.v(sim.s) > n.stake_0]

        if len(under) > 0:
            v_loss = np.array([n.v(sim.s) - n.stake_0 for n in under])
            self.avg_loss = np.mean(v_loss)
        else:
            self.avg_loss = 0

        if len(over) > 0:
            v_gain = np.array([n.v(sim.s) - n.stake_0 for n in over])
            self.avg_gain = np.mean(v_gain)
        else:
            self.avg_gain = 0

        self.under_target =  len(under)/len(sim.nodes)
        self.over_target  = len(over)/len(sim.nodes)

    def mk_row(self):
        """to be called after set_finals will return the csv string for
        current cached values"""
        return self.prefix + ",".join (
            [str (np.round (self.__getattribute__(k),10))
             for k in EpisodeStats.response_keys]) + "\n"

def fill_in_fns (ps):
    """
    Transform parameters with pointers to class and functions
    """
    stake_f = stake_f_label_to_fn [ps['stake_f']]
    sim_c =  sim_label_to_class [ps['sim']]
    return {**ps,**{'stake_f':stake_f, 'sim':sim_c}}


@unverbosed
def boot_exp(params,
             out_fn=sys.stdout.write,
             header=True):
    """Bootstrap experiment, builds a simulation forawrding kwargs in
    params to the appropriate Simulation extension constructor.

    The simulation is repeated `times` times, and dumps stats produced
    by `EpisodeStats` via `out_fn`.

    """

    times = params ['times']

    psf = fill_in_fns (params) # resolve sim class and stake_f
    _class = psf ['sim']

    stats = EpisodeStats(params) # init. aggregator
    if header:
        out_fn(EpisodeStats.header)  # dump header

    for i in range(times): # repeat the simulaion
        sim = _class(**psf) # build and run sim
        stats.set_init(sim)
        sim.run() # run the simulation
        stats.set_finals(sim)
        out_fn(stats.mk_row()) # dump rep. stats
