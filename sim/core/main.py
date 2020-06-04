import argparse
import sys
from sim.core.batch import run_batch, long_form_results

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
    help='Generator function for inital stake distrib. (eq | beta | pareto)')

parser.add_argument(
    '--sim',
    required=True,
    help='Indicate simulator class (random | const | geom | log_const | log_geom )')


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
    args_dict['R'] = args_dict['c'] * float(args_dict['T'])
    run_batch (args_dict,out_fn)

def main ():
    """
    Parse arguments from argv,
    run the batch and print the results to stdandard output
    """
    args = parser.parse_args ()
    args_dict = args.__dict__
    run(args_dict)


if __name__ == "__main__":
    main ()
