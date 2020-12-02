# base_object.py
"""
Abstract class for simulation objects
=====================================

"""
from IPython.display import Math, Latex, display
import abc
import pprint as pp

from sim.core.decorators import *

class BaseObject():
    """Foundation class for objects in the simulation.
    Offers a class variable indicating which slots
    should not be included in the object `params` dict.
    Offers id generation facility at the class level.
    """
    # omit these fiels in params() method for serialization
    blackList = []

    # dynamic class variable used to assign unique ids to all base objects
    # not that this will be a new one for extending classes
    id = 0
    # Extending classess may also change the prefix to use for their ids
    id_prefix = ""
    # the next id for any extending class can be obtained by
    def next_id(self):
        # note that this is an instance method, to allow to
        # define at this level, the genertion for any extension
        t = type(self)
        id = t.id
        t.id += 1
        return t.id_prefix + str(id)

    def __init__(self):
        self.id = type(self).next_id(self)

    def dict(self,**kwargs):
        """ Return self.__dict__ """
        return self.__dict__

    def params(self,**kwargs):
        "Similar to `dict` but excludes some blacklisted items"
        return {k:v for (k,v)
                in self.dict(**kwargs).items()
                if k not in self.blackList}

    def __repr__(self):
        return f'<{type(self)}: \n{pp.pformat(self.__dict__,indent=4)}>'

    @abc.abstractmethod
    def log(self,*args,**kwargs):
        raise Exception("log is not implemented for class: {}".format(type(self)))


def display_objects(os,*args,**kwargs):
    display([o.dict(*args,**kwargs) for o in os])

def display_objects_params(os,*args,**kwargs):
    display([o.params(*args,**kwargs) for o in os])




###### END #####
