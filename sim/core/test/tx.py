import numpy as np

def norm(x):
    tot = sum(x)
    return [y/tot for y in x]

stakes = [1,2,3,4]
vs= norm(stakes)


def txlin(xs,m):
    txs = [x * m for x in xs]
    return txs
    #return norm(txs)

def nonlin(x,m,b):
    return x*m - (b*np.exp(x)-b)

def txnonlin(xs,m,b):
    txs = [nonlin(x,m,b) for x in xs]
    return norm(txs)
