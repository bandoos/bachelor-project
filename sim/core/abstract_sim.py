from sim.core.base_object import *
from sim.core.plot import *
from sim.core.decorators import *
import abc

class AbstractSimulation(BaseObject):
    """Encapsulates aspects shared by all concrete simulations.
    Including a default logging function, self.T (max epochs)
    self.t (initial/current epoch) = 0, self.s (current total stake),
    self.nodes (container for simulation agents),
    blacklisting nodes for params(), some basic plotting for the nodes
    """
    id_prefix = "sim-"
    blackList = ["nodes","w_history","s_history","r_history"]

    def __init__(self,nodes,T,s):
        super().__init__()
        # nodes container
        self.nodes = nodes
        # init instance state
        self.T = T
        self.s = s
        self.t = 0

        # allow nodes to register their initial fractional stake
        self.step_all_nodes()

        # History slots
        self.w_history = []
        self.s_history = [self.s]
        self.r_history = []

    def step_all_nodes(self):
        """Invokes ste step method for all nodes in self.nodes """
        for node in self.nodes:
            node.step(tot=self.s)

    @abc.abstractmethod
    def select_proposer(self):
        """Method to be overriden to implement proposer selection procedure"""
        raise Exception("select_proposer must be specialized for: {}".format(type(self)))

    @abc.abstractmethod
    def give_reward(self,node):
        """Method to be overriden to implement reward mechanism"""
        raise Exception("give_reward must be specialized for: {}".format(type(self)))

    def step(self):
        """Runs a full iteration oif the simulation.
        This method should not be overriden, it uses the overridable methods
        defining the common sequence of operations
       """

        self.log("Step begins.")

        chosen = self.select_proposer() # chose proposer
        self.log("Selected proposer: ", chosen.id)
        self.w_history.append(chosen.id) # record chosen W(n)

        rew = self.give_reward(chosen) # reward proposer
        self.log("Reward computed: ", rew)
        self.r_history.append(rew) # record reward

        self.s += rew # add the freshly minted reward also to the total stake
        self.log("New total stake: ", self.s)
        self.s_history.append(self.s) # record new total stake

        # allow nodes to record their new fractional stake
        self.step_all_nodes()

        self.t += 1
        return self

    def run(self):
        """Run all the simulaion iterations via .step()."""
        while self.t < self.T:
            self.log("------------")
            self.step()
        return self

    def log(self,*args,**kwargs):
        """Default log facility. uses sim.core.decorators.vprint to
        conditionally report simulation info

        """
        vprint("<{} [t:{}/{}]>".format(self.id, self.t, self.T-1),
                   *args,**kwargs)

    # the following methods allow to visualize fractional stake
    # distribution of a simulation's node directly passing the current
    # total sake as `tot` argument, and forwarding additional kwargs
    # to the plotter functions
    def plot_nodes_bar(self,**kwargs):
        bar_plot_nodes(self.nodes,tot=self.s, **kwargs)

    def plot_nodes_hist(self,**kwargs):
        hist_nodes(self.nodes,tot=self.s,**kwargs)

    def plot_nodes_dist(self,**kwargs):
        dist_nodes(self.nodes,tot=self.s, **kwargs)

    # Deprecated (memroy expensive) node history plot

    # def plot_nodes_v(self):
    #     x = range(self.T+1)
    #     for v_hist in [n.v_hist for n in self.nodes]:
    #         plt.plot(x,v_hist)
