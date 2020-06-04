import numpy as np
import math
import sys

from time import time
from functools import *

from sim.core.sim_0 import Simulation
from sim.core.decorators import *

from sim.core.stake_f import stake_f_label_to_fn
from sim.core.sim_0 import Simulation
from sim.core.random_sim import RandomSim
from sim.core.logcont_sim import LogConstSim
from sim.core.geom_sim import GeomSim, LogGeomSim

sim_label_to_class ={
    'random':  RandomSim,
    'const':   Simulation,
    'log_const': LogConstSim,
    'geom': GeomSim,
    'log_geom': LogGeomSim,
}

def gini_coeff(pop):
    mu = np.mean(pop)
    n2 = len(pop)**2
    diffsum = sum([abs(x - y) for x in pop for y in pop])
    return diffsum/(2*n2*mu)

class EpisodeStats():
    indep_keys = ["m","T","c","R","sim","stake_f"]
    response_keys = ["var_0","var_T",
                     "gini_0","gini_T",
                     "under_target","avg_loss",
                     "over_target","avg_gain"]

    header = ",".join ([*indep_keys,*response_keys]) + "\n"

    def __init__(self,params):
        self.prefix = ",".join ([str (params [k])
                                 for k in EpisodeStats.indep_keys]) + ","

    def set_init(self,sim):
        init_vs = [n.stake for n in sim.nodes] # initial stakes are already fractional
        self.gini_0 = gini_coeff(init_vs)
        self.var_0 = np.var(init_vs)

    def set_finals(self,sim):
        final_vs = [d.v(sim.s) for d in sim.nodes] # get final fractional stakes

        self.gini_T= gini_coeff(final_vs) # compute final stats
        self.var_T = np.var(final_vs)

        under = [n for n in sim.nodes # who was penalized by the process
                 if n.v(sim.s) < n.stake_0]
        over = [n for n in sim.nodes # who was favored by the process
                if n.v(sim.s) > n.stake_0]

        v_loss = np.array([n.v(sim.s) - n.stake_0 for n in under])
        self.avg_loss = np.mean(v_loss)

        v_gain = np.array([n.v(sim.s) - n.stake_0 for n in over])
        self.avg_gain = np.mean(v_gain)

        self.under_target =  len(under)/len(sim.nodes)
        self.over_target  = len(over)/len(sim.nodes)

    def mk_row(self):
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


## Bootstrap an experiment,
## all `params` will be directly spliced in `sim_class`
## constructor so exact keys depend on that,
@unverbosed
def boot_exp(params,out_fn=sys.stdout.write):
    """Bootstrap experiment, builds a simulation forawrding kwargs
    in params to the Simulation constructor,
    The simulation is repeated `times` times, and
    dumps stats as per above class
    """

    times = params ['times']

    psf = fill_in_fns (params) # resolve sim class and stake_f
    _class = psf ['sim']

    stats = EpisodeStats(params)
    out_fn(EpisodeStats.header)

    for i in range(times):
        sim = _class(**psf) # build and run sim
        stats.set_init(sim)
        sim.run() # run the simulation
        stats.set_finals(sim)
        out_fn(stats.mk_row())
