from sim.executor.batch.ibatch import *

# P introduces a cartesian product

# each combination of params is repeated
# REPETITIONS times per simulaion (i.e. within the same PID)

REPETITIONS=25

# an additional multiplier called REDUNDANCY
# controls external redundancy (i.e. with a different PID, possibly in parallel)

REDN_N=1
REDUNDANCY=range(REDN_N)

# This yields a total of REPETITIONS * REDN_N simulations
# per parameter combination

batch = \
    P({'m':  [10 ** i for i in range(1,4)],
       'T':  [10 ** i for i in range(1,4)],
       'c':  [0.001, 0.01, 0.1, 0.5, 1, 2, 10, 100],
       'sim':        ['const','geom','log_const','log_geom','random'],
       'stake_f':    ['eq','beta','pareto'],
       'times':      [REPETITIONS],
       'redundancy': REDUNDANCY })


if __name__ == "__main__":
    import pprint
    _batch = batch()

    pprint.pprint({'lenght':len(_batch),
                   'body':batch.dic})
