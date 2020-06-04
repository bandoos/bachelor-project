# decorators.py
# utilities for verbosity and brevity

from pprint import pprint

verbose = True
def vprint(*a,**k):
    global verbose
    if verbose:
        print(*a,**k)

def vpprint(a):
    global verbose
    if verbose:
        pprint(a)

## A decorator to make sure a piece of code
# does not print verbose statements even if
# the verbose global tells to do so.
def unverbosed(f):
    global verbose
    def decorated(*args,**kwargs):
        global verbose
        ov = verbose
        verbose = False
        r = f(*args,**kwargs)
        verbose = ov
        return r
    return decorated

def verbosed(f):
    global verbose
    def decorated(*args,**kwargs):
        global verbose
        ov = verbose
        verbose = True
        r = f(*args,**kwargs)
        verbose = ov
        return r
    return decorated

## Sometimes i want to see the notebook without tests and demos,
# the following decorator makes sure that when `do_demos` is false,
# decorated functions do not execute
do_demos = True
def demofunc(f):
    global do_demos
    def decorated(*args,**kwargs):
        global do_demos
        if do_demos:
            return f(*args,**kwargs)
        else:
            print("Execution of func: [{}] was suppressed by the `do_demos` global option".format(f.__name__))
    return decorated
