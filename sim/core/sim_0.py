# sim_0
from random import choices

from sim.core.decorators import *
from sim.core.abstract_sim import *
from sim.core.stake_f import *
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

    - self.r reward function $r(n)$ constant at self.R/T, this is
      labeled "R/T"

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

        # default reward function is constant R/T
        self.r = lambda _: self.R/self.T # function used to determine reward

        # logging
        self.log("Initialised simulation: ")
        vpprint(self.params())

    def select_proposer(self):
        """Basic block proposer selection:
        Choose only 1 node with a prob. eq. to their fractional stake
        """
        probs = [ n.stake for n in self.nodes ] # directly use stake frac.
        chosen = choices(self.nodes, probs, k=1)[0] # draw 1 from this urn
        return chosen

    def give_reward(self,node):
        """ uses self.r (reward function) to emit reward for
        the current epoc to the given node instance.
        """
        rew = self.r(self.params()) # compute reward for this timestep
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
            'r': 'R/T', # textually reprsents the default function
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
    ```@with_reward_fn(fun)
       class SomeClass(Simulation):
           ...
           pass```

    """

    def d(c):
        setattr(c,'r',fn)
        return c
    return d


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
