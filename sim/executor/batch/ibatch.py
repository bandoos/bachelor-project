import itertools as it
import abc
import dataclasses as d
from pprint import pprint
import functools as fp

class MExpander(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, '__call__') and
                callable(subclass.__call__))


def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True

def m_expandable(obj):
    return issubclass(type(obj),MExpander)

def expandable(obj):
    return iterable(obj) or m_expandable(obj)

class _Expandable(object):
    def __init__(self,o):
        self.o=o

    def __call__(self,env={}):
        return self.o if iterable(self.o) else self.o()

    def __enter__(self):
        if not (m_expandable(self.o) or iterable(self.o)):
            raise Exception(f'Parse error {self.o} is not expandable')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.o

class _Iterable(object):
    def __init__(self,o):
        self.o=o
        self.i=None


    def __enter__(self):
        try:
            self.i = iter(self.o)
        except Exception:
            raise Exception(f'Parse error {self.o} is not iterable')

        return self.i

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.o
        del self.i


def do_expand(x):
    with _Expandable(x) as f:
        with _Iterable(f()) as i:
            return i

@d.dataclass
class Li():
    """ List constructor that will expand its elements.  """
    vs : list

    def __call__(self,env={}):
        return self._expand(env)

    def _expand(self,env={}):
        ys = map(do_expand, self.vs)
        return list(fp.reduce(lambda x,y:[*x,*y], ys))

    def __add__(self,expander):
        return Li([self,expander])

# * The P constructor

# list(it.product([1,0],[1,0]))
# ** helper function
def dict_product(dic):
    ks = list(dic.keys())
    vals = list(it.product(*[dic[k] for k in ks]))
    out = []
    for tup in vals:
        out.append(dict(zip(ks,tup)))
    return out

# a = {'a':[1,2,3],
#      'b':[-1,-2,-3]}

# dict_product(a)

@d.dataclass
class P():
    """ Defines key wise cartesian expansion.
    {'b':Vs}
    """
    dic : dict

    def __call__(self,env={}):
        return self._expand(env)

    def _expand(self,env={}):
        new = dict(self.dic)
        for k in self.dic:
            new[k] = do_expand(self.dic[k])
        return dict_product(new)

    def __add__(self,expander):
        return Li([self,expander])






# We can test that a class satisfies the formal interface
# issubclass(P, MExpander)

# issubclass(Li, MExpander)

# Deprecated:

@d.dataclass
class Vs():
    """Vs will not expand, its children Pretty useless now that we support
    iterables as expandable(s).  Remains an example of how to
    implement otherwise.

    DEPRECATED: use a simple list or tuple instead

    """
    vs : list

    def __call__(self,env={}):
        return self._expand(env)

    def _expand(self,env={}):
        return self.vs
