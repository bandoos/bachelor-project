"""
command line argument parser module
===================================

defines the argparse instance `parser`

for the main module

"""
import argparse

# * Setup arguments parser
parser = argparse.ArgumentParser(description='Run a sim-stake-batch')

parser.add_argument('--id',
                    required=False,
                    default=0,
                    help='unique id for the experiment')

requireNamed = parser.add_argument_group('required arguments')


requireNamed.add_argument('--m',
                    type=int,
                    required=True,
                    help='INTEGER: Indicate the number of nodes [m] (valid if >= 2)')

requireNamed.add_argument('--T',
                    type=int,
                    required=True,
                    help='INTEGER: Indicate max epoch time [T] (valid if >= 2)')

requireNamed.add_argument('--c',
                    type=float,
                    required=True,
                    help='FLOAT: Indicate total load factor "c" [R=cT] (valid if > 0)')


requireNamed.add_argument('--times',
                    type=int,
                    required=True,
                    help='INTEGER: Redudancy factor (valid if > 0)')

requireNamed.add_argument(
    '--stake_f',
    required=True,
    choices=['eq','beta','pareto'],
    help='STRING: Generator function for inital stake distrib.')

requireNamed.add_argument(
    '--sim',
    required=True,
    choices=['random','const','geom','log_const','log_geom'],
    help='STRING: Indicate simulator class')
