#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete
import sys

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


argcomplete.autocomplete(parser)

from sim.core.batch import run_batch, long_form_results


# Test the argumet parser
def test_0():
    args = parser.parse_args(["--m", "5",
                              "--T", "1000",
                              "--c", "0.1",
                              "--sim", "random",
                              "--stake_f", "eq",
                              "--times", "300"])
    return args

# * Main function

def run(args_dict,out_fn=sys.stdout.write):
    """Run a full simulation for parameters in args_dict.
    if not provided out_fn defaults to writing to stdout.
    The value of args_dict['R'] will be computed as c*T.

    Relies on run_batch after adding R to the dict, forawrding out_fn

    """
    args_dict['R'] = args_dict['c'] * float(args_dict['T'])
    run_batch (args_dict,out_fn)

def main ():
    """
    Parse arguments from argv,
    uses `run` to execute the batch and prints the results to stdandard output.

    Invoked when __name__ == "__main__".
    """
    args = parser.parse_args ()
    args_dict = args.__dict__
    run(args_dict)


if __name__ == "__main__":
    main ()
