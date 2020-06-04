import numpy as np
from random import choices

m = 10
r = 1

nodes = [{"id":i,"v":1/m} for i in range(m)]

def under():
    return len([n for n in nodes if n["v"] < 1/m])/m

def under_avg():
    return np.mean([1/m - n["v"] for n in nodes if n["v"] < 1/m])


def above():
    return len([n for n in nodes if n["v"] > 1/m])/m

def above_avg():
    return np.mean([n["v"] - 1/m  for n in nodes if n["v"] > 1/m])

def tot():
    return sum([n["v"] for n in nodes])

def norm():
    t = tot()
    for i in range(m):
        nodes[i]["v"] /= t

def select_proposer():
    probs=[1/m for _ in nodes]
    chosen = choices(nodes,probs,k=1)[0]
    return chosen["id"]


def run(epochs):
    for e in range(epochs):
        chosen = select_proposer()
        nodes[chosen]["v"] += r

    norm()
    print(under(),"   ", above())
    print(under_avg(),"   ", above_avg())


run(1000)
