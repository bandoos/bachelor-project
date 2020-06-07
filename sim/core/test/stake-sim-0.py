"""
interactive test/demo
===========================

"""



import numpy as np
import scipy.stats as st
import types

from functools import *
from matplotlib import pyplot as plt
from pprint import pprint
# import seaborn
import seaborn as sns
# settings for seaborn plotting style
#sns.set(color_codes=True)
# settings for seaborn plot sizes
#sns.set(rc={'figure.figsize':(5,5)})


from IPython.display import Math, Latex, display

plt.style.use("seaborn-dark")

#from widgets import *

# local imports
from sim.core.plot import *
from sim.core.decorators import *
from sim.core.base_object import *
from sim.core.node import *
from sim.core.abstract_sim import *
from sim.core.sim_0 import *
from sim.core.stake_f import *

@demofunc
def demo_node():
    # build 2 nodes with initial stake 0.5
    node = Node(0.5)
    node1 = Node(0.5)
    # display, passing a tot arg
    display(node.dict(tot=1))
    display(node1.dict(tot=1))
    # add stake
    print("Applying new stake")
    (node + 0.5 + 0.25) + 0.25 # this modifies the node in place
    display(node.dict(tot=2))
    display(node1.dict(tot=2))


demo_node()

## stake functions are defines in the stake_f.py module
eq_stake_f(0,10) # 0 being the (in this case bogus) index

@demofunc
def demo_unif():
    "Build show and return 3 nodes with equal initial stake"
    nodes_unif = make_nodes(3,
        eq_stake_f
    )
    for node in nodes_unif:
        # note that dict requires the total stake (initially 1) to compute v
        print(node.dict(tot=1))
    return nodes_unif

nodes_unif = demo_unif()

@demofunc
def demo_bar_plot(nodes):
    display_objects(nodes,tot=tot_stake(nodes))
    bar_plot_nodes(nodes)

demo_bar_plot(nodes_unif)


@demofunc
def test_quad():
    nodes_quad = make_nodes_norm(10,quad_stake_f)
    plot_bar_and_dist(nodes_quad,hist_bins=7)
    #kde_nodes(nodes_quad)
    #display_objects(nodes_quad,tot=tot_stake(nodes_quad))

test_quad()

@demofunc
@unverbosed
def test_gamma_1():
    nodes_gamma = make_nodes_norm(100,gamma_stake_f_1)
    plot_bar_and_dist(nodes_gamma)

test_gamma_1()

r_const_1 = lambda _: 1

r_f_map = {
    r_const_1 : 'const_1'
}

@demofunc
def test_simple_sim():
    sim = Simulation(T=100,m=10,stake_f=eq_stake_f)
    sim.plot_nodes_bar()
    return sim

sim = test_simple_sim()

@demofunc
@unverbosed # avoid producing verbose output with 100 nodes in it
def test_gamma_1_sim():
    sim = Simulation(m=100,T=100,
                     stake_f=gamma_stake_f_1)
    sim.plot_nodes_dist()
    display(sim.params())
    return sim

sim_gamma = test_gamma_1_sim()

@verbosed
@demofunc
def demo_select_proposer(sim):
    sim.select_proposer()
    display_objects_params([sim])
demo_select_proposer(sim)

@verbosed
@demofunc
def demo_reward(sim):
    winner = sim.select_proposer()
    sim.give_reward(winner)
    display_objects_params([sim])
demo_reward(sim)

@verbosed
@demofunc
def demo_step():
    sim = Simulation(T=3,R=3)
    sim.run()
    return sim
sim = demo_step()

m = 3
T = 1000
R = 1000
print("m:",m,"T:",T,"R:",R)

@unverbosed
@demofunc
def demo_step(m,T,R):
    sim = Simulation(m=m,T=T,R=R,stake_f=eq_stake_f)
    sim.run()
    return sim
sim = demo_step(m,T,R)
#sim.plot_nodes_v()

sim.plot_nodes_dist()
