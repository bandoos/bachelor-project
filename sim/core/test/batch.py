"""
Batch results formatting module
===============================



"""
import sys
import numpy as np
#from pprint import pprint

from sim.core.boot_exp import boot_exp
# Map argument labels to simulation classes

## Assume ps is parsed from command line args
## First we need a dict mapping from stake_f labels
## to stake_f, same for sim Class

# NOTE that the sim_class itself is to be considered as a param,
# namely indicating reward mechanism and also selection transform
# function, can be a separate predictor RAND. LIN. LOG.
parsed_args = { 'm':10,
                'T':1000,
                'R':500,
                'stake_f':"eq",
                'sim':"random",
                'id':0,
                'times':300,
                'color':'green'}



# # Expand the results to produce a csv
# def long_form_results (results):
#     """
#     Produce a csv string from the innput dictionary
#     """
#     indep_keys = ["m","T","c","R","sim","stake_f"] # remove exp_v_T as can be derived
#     response_keys = ["mu_h",
#                      "var_0_h","var_h",
#                      "gini_0_h","gini_h",
#                      "under_target_h","avg_loss_h",
#                      "over_target_h","avg_gain_h"]

#     s = ",".join ([*indep_keys,*response_keys]) + "\n"
#     prefix = ",".join ([str (results [k]) for k in indep_keys]) + ","
#     for time in range (results ['times']):
#         s += prefix + ",".join ([str (np.round (results [k] [time],8))
#                                   for k in response_keys]) + "\n"

#     return s




def run_batch(ps,out_fn=sys.stdout.write):
    """Given a parameters dictionary boot up an experiment, Returns a
    dictionary which is the parameters merged with the experiment
    result. `long_form_results` can be used to produce a csv string of
    the results

    """
    boot_exp (ps,out_fn)
