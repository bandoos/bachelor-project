# decorators.py
"""
decorators
==========

utilities for verbosity and brevity

"""
from functools import wraps
from pprint import pprint

verbose = True
def vprint(*a,**k):
    """
    like `print` but suppressed when global verbose = False
    """
    global verbose
    if verbose:
        print(*a,**k)

def vpprint(a):

    """
    like `pprint.pprint` but suppressed when global verbose = False
    """
    global verbose
    if verbose:
        pprint(a)

def unverbosed(f):
    """A decorator to make sure a piece of code DOES NOT print verbose
    statements even if the verbose global tells to do so.

    """
    global verbose
    @wraps(f)
    def decorated(*args,**kwargs):
        global verbose
        ov = verbose
        verbose = False
        r = f(*args,**kwargs)
        verbose = ov
        return r
    return decorated

def verbosed(f):
    """A decorator to make sure a piece of code DOES print verbose
    statements even if the verbose global tells not to do so.

    """
    global verbose
    @wraps(f)
    def decorated(*args,**kwargs):
        global verbose
        ov = verbose
        verbose = True
        r = f(*args,**kwargs)
        verbose = ov
        return r

    return decorated

do_demos = True
def demofunc(f):
    """
    the following decorator makes sure that when `do_demos` is false,
    decorated functions do not execute
    """
    global do_demos
    @wraps(f)
    def decorated(*args,**kwargs):
        global do_demos
        if do_demos:
            return f(*args,**kwargs)
        else:
            print("Execution of func: [{}] was suppressed by the `do_demos` global option".format(f.__name__))

    return decorated
