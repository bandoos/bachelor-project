"""
Utilities module
================

"""

#!pip install --user tabulate
import tabulate
import numpy as np
from IPython.display import Math, Latex,HTML, display

def rnd(n,places=5):
    return round(n,places)

def show_math(*strings):
    for string in strings:
        display(Math(string))

def show_latex(*strings):
    for string in strings:
        display(Latex(string))

rm_id = lambda k,id='exp_id': list(filter(lambda x: x != 'exp_id',k))

def summarize(res,keys,
              id_key="exp_id",
              fs=[("mu",np.mean),
                  ("var",np.var)]
             ):
    """Summarize a dict. of results.
    Input: a dict `res`, which should contain
    for each key in keys a list of numbers.
    Output: produces a new dictionary, keeping the `id_key` field,
    and summarising the data of `keys`
    for each function in fs.
    Fs should be a list of tuples (name,func).
    """
    summary =  { k: {
        ft[0]: ft[1](res[k]) for ft in fs
    } for k in rm_id(keys)}

    return {"exp_id":res['exp_id'],**summary}



def to_lists(results,keys,subkey,id_key="exp_id"):
    """Given a list of summarized results,
    return a table, with header the 'exp_id' of each
    result, and one row per metric in keys.
    Note since records in a result are dicts themsevels,
    the `subkey` is used to access the inner dict.
    """
    first_row = ["metric ({})".format(subkey),*[r[id_key] for r in results]]
    d = {k:[] for k in keys}
    for res in results:
        for key in keys:
            d[key].append(rnd(res[key][subkey]))
    display(d)
    return [first_row,
        *[[key,*d[key]] for key in keys]]

def show_table(lis):
    display(HTML(tabulate.tabulate(lis,tablefmt='html',
                                  headers='firstrow')))
