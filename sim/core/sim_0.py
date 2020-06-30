"""
Default concrete simulaion
=================================

Defines the basic concrete class for simulation extensions

Extensions are defined in sim.core.implem.py module

"""
from random import choices

from sim.core.decorators import *
from sim.core.abstract_sim import *
from sim.core.stake_f import *
from sim.core.sel_f import selection_fn_mappings
from sim.core.rew_f import rew_fn_mappings
from sim.core.node import *

class Simulation(AbstractSimulation):
    """A first extension of the AbstractSimulation.
    Provides:

    - default self.T = 100

    - defualt self.s (initial/current total stake) = 1

    - default self.R (total rewards) = 100

    - default number of nodes m = 3

    - nodes generation accoding to self.m and:

    - default self.stake_f, used to generate intial stake distrib.

    Reward function `type(self).r` and selection mechanism `self.select_proposer` should still be implemented
    by extensions of this class

    """

    def __init__(self,
                 T=100,
                 m=3,
                 R=100,
                 stake_f=eq_stake_f,
                 **kwargs):

        self.m = m
        nodes = make_nodes_norm(m,stake_f)
        # since we norm. init. stake, we pass s=1 as initial total stake
        super().__init__(nodes,T,s=1)

        # additional slots
        self.R = R # fixed ammount of total reward over the period T

        # function slots
        self.stake_f = stake_f # function used to generate initial distribution of stake

        # logging
        self.log("Initialised simulation: ")
        vpprint(self.params())


    def give_reward(self,node):
        """ uses type(self).r (reward function) to emit reward for
        the current epoch to the given node instance.
        """
        rew_fn = type(self).r
        if rew_fn  is None:
            raise Exception(f'Reward function {type(self)}.r was never set!')
        rew = rew_fn(self.params()) # compute reward for this timestep
        self.log("r(n) = ", rew)
        node + rew # give reward to target node
        return rew

    # Helper methods
    # override
    def dict(self,**kwargs):
        "Reprsesent Simulation as dict."
        return {
            **self.__dict__,
            'stake_f': stake_f_map[self.stake_f],
            'sel_f': selection_fn_mappings[type(self).select_proposer],
            'rew_f': rew_fn_mappings[type(self).r],
            'nodes': [ n.dict(tot=self.s) for n in self.nodes ]
        }

def make_nodes(n,stake_f):
    """Produce a set of nodes of size n, according to stake_f.
    The stake function will be passed the index and n while generating,
    and is responsible for assigning initial stake.
    An optional prefix may be given for id generation.

    This function should not be used directly, use make_nodes_norm
    which ensures sum of results is = 1

    """
    vprint("Producing ", n, "nodes with stake_f: ",stake_f)
    return [ Node(stake_f(i,n))
            for i in range(n) ]

def make_nodes_norm(n,stake_f):
    """ Same as make_nodes but ensures sum of initial stakes is 1"""
    nodes = make_nodes(n,stake_f)
    vprint("Normalizing initial stake...")
    tot = sum([d.stake_0 for d in nodes])
    for node in nodes:
        node.stake = node.stake/tot
        node.stake_0 = node.stake
    return nodes


def with_reward_fn(fn):
    """Decorator for simulation implementation classes.

    Acts at the class level setting the 'r' attribute to
    the given reward fucntion

    Usage: use as decorator passing the desired reward function
    """

    def d(c):
        setattr(c,'r',fn)
        return c
    return d

'''
@with_reward_fn(fun)
class SomeClass(Simulation):
    pass

'''

def with_selection_fn(fn):
    """Same as for with_reward_fn but for the selection
    procedure.

    Acts at the class level setting the 'select_proposer' attribute to
    the given selection fucntion

    """
    def d(c):
        setattr(c,'select_proposer',fn)
        return c
    return d
