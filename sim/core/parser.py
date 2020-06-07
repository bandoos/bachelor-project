"""
command line argument parser module
===================================

defines the argparse instance `parser`

for the main module

"""
import argparse

# * Setup arguments parser
parser = argparse.ArgumentParser(description='Run a sim-stake-batch')

parser.add_argument('--m',
                    type=int,
                    required=True,
                    help='Indicate the number of nodes [m]')

parser.add_argument('--T',
                    type=int,
                    required=True,
                    help='Indicate max epoch time [T]')

parser.add_argument('--c',
                    type=float,
                    required=True,
                    help='Indicate total reward coefficietn [R=cT]')

parser.add_argument('--id',
                    required=True,
                    help='unique id for the experiment')

parser.add_argument('--times',
                    type=int,
                    required=True,
                    help='Redudancy factor')

parser.add_argument(
    '--stake_f',
    required=True,
    choices=['eq','beta','pareto'],
    help='Generator function for inital stake distrib.')

parser.add_argument(
    '--sim',
    required=True,
    choices=['random','const','geom','log_const','log_geom'],
    help='Indicate simulator class')
