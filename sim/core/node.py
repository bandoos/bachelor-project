"""
Module implementing simulation entities `Node` reprsenting
validator nodes of the blockchain.

"""

import numbers

from sim.core.base_object import *
from sim.core.decorators import *

class Node(BaseObject):
    """Node class reprsents stake holders.
    Very simple design, stores current absolute, stake
    and a list of historical values for v, the fractional
    stake (absolute/total).

    Note that storing history can be very memory expensive,
    so it must be explicitly enabled passing save_history=True

    """

    id_prefix = "node-"
    # Node has no blacklisted slot by now


    def __init__(self,stake_0,save_history=False):
        """Build the node with initial stake_0"""
        super().__init__()
        vprint("Initializing node: ", self.id, "with stake: ",stake_0)
        self.stake_0 = stake_0 # save inital stake
        self.stake = stake_0
        self.v_hist = [] if save_history else None

    def step(self,**kwargs):
        "Add a value to the historical v"
        if self.v_hist:
            self.v_hist.append(self.v(kwargs['tot']))
        return self

    def v(self,tot):
        "Returns the fractional stake WRT to tot of this player"
        return (self.stake/tot)

    # override
    def dict(self,**kwargs):
        "Represent node as dict. requires passing the current total stake."
        if not 'tot' in kwargs.keys():
            raise Exception("Missing `tot` kwarg when generating dict for {}".format(self))
        return {**self.__dict__,
                'v':self.v(kwargs['tot'])}

    # op overloading
    def __add__(self,o):
        "Adding a numeric value to a node means incrementing stake"
        if isinstance(o,numbers.Number):
            self.stake += o
            return self
        else:
            raise Exception("Cannot __add__ [{}] to Node instance: {}"\
                  .format(o,self))
