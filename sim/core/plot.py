from matplotlib import pyplot as plt
import seaborn as sns
from functools import *

# NOTE: for the following function,
# if the optional arg `tot` is not provided,
# then it is calculated from the sum of stake of the each node
# using the following function
tot_stake = lambda nodes: reduce(lambda x,y: x + y.stake, nodes,0)

def bar_plot_nodes(nodes,tot=None):
    "Plot nodes fractional stake as a bar-plot"
    if tot is None:
        tot = tot_stake(nodes)
    plt.bar(range(len(nodes)),[ d.v(tot) for d in nodes])

def hist_nodes(nodes,
               bins=20,
               tot=None):
    "Plot an histogram of nodes frac. stake."
    if tot is None:
        tot = tot_stake(nodes)
    plt.hist([d.v(tot) for d in nodes],bins=bins)


def plot_kde(values,
                bins=30,
                xlab="frac. stake.",
                ylab="Frequency",
                kernel='gau',
            **kwargs):
    ax = sns.distplot(values,
                  bins=bins,
                  kde=True,
                  kde_kws={'kernel':kernel},
                  color='green',
                  hist_kws={
                      "color":"skyblue",
                      "linewidth": 15,
                      'alpha':1
                  },
                   **kwargs)
    return ax.set(xlabel=xlab, ylabel=ylab)


def kde_nodes(nodes,
                bins=30,
                xlab="frac. stake.",
                ylab="Frequency",
                tot=None):

    if tot is None:
        tot = tot_stake(nodes)
    ax = sns.kdeplot([d.v(tot) for d in nodes],
                  color='skyblue')
    return ax.set(xlabel=xlab, ylabel=ylab)

def dist_nodes(nodes,bins=30,
               xlab="frac. stake.",
               ylab="Frequency",
               tot=None):
    "Plot the distribution of fractional stake via kernel estimation density"
    if tot is None:
        tot = tot_stake(nodes)
    return plot_kde([d.v(tot) for d in nodes],
            bins=bins)


def plot_bar_and_dist(nodes,hist_bins=20):
    "Plot side by side the bar plot and the dist plot of the nodes"
    plt.subplot(1, 2, 1)
    bar_plot_nodes(nodes)
    plt.subplot(1,2,2)
    dist_nodes(nodes,bins=hist_bins)


def add_vlines(*xs,**kwargs):
    min,max = plt.gca().get_ylim()
    plt.vlines(*xs,min,max,**kwargs)

def add_hlines(*ys,**kwargs):
    min,max = plt.gca().get_xlim()
    plt.hlines(*ys,min,max,**kwargs)
