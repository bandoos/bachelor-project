from sim.executor.batch.ibatch import *

# P introduces a cartesian product

# each combination of params is repeated
# REPETITIONS times per simulaion (i.e. within the same PID)

REPETITIONS=100

# an additional multiplier called REDUNDANCY
# controls external redundancy (i.e. with a different PID, possibly in parallel)

REDN_N=4
REDUNDANCY=range(REDN_N)

# This yields a total of REPETITIONS * REDN_N simulations
# per parameter combination

batch = \
    P({'m':[10,100],
       'T':[365],
       'c':[1],
       'sim':['const','geom'],
       'stake_f':['eq'],
       'times':[REPETITIONS],
       'redundancy': REDUNDANCY })


if __name__ == "__main__":
    import pprint
    _batch = batch()
    pprint.pprint({'lenght':len(_batch),
                   'body': batch.dic})
