import numpy as np
from random import choices
# * Proposer selection implementations

# ** Rand
def random_proposer_selection(self):
    """ Overrides selection procedure to sample nodes
    randomly with eqaul probability """
    # probs = [1/self.m for _ in range(self.m)]
    return choices(self.nodes,k=1)[0] # equiprobable is the default

# ** Linear
def linear_proposer_selection(self):
    """Basic block proposer selection:
    Choose only 1 node with a prob. eq. to their fractional stake
    """
    probs = [ n.stake for n in self.nodes ] # directly use stake.
    chosen = choices(self.nodes, probs, k=1)[0] # draw 1 from this urn
    return chosen

# ** Log
def log_proposer_selection(self):
    """Implementation of the logarithmic proposer selection function.
    Note that the base of the log is irrelavant since the vector
    of logs will be normalized.

    Uses random.choices with weights vector determined
    by log(1 + x).

    Returns a single node as result.

    """

    # TODO make it np.log(1 + np.array([...]))
    probs=np.array([np.log(1 + n.v(self.s)) for n in self.nodes])
    return choices(self.nodes,probs,k=1)[0]

selection_fn_mappings = {
    random_proposer_selection: 'sel_rand',
    linear_proposer_selection: 'sel_lin',
    log_proposer_selection: 'sel_log',
}
