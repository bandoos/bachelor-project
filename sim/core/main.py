#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK

"""
Main module
===========

Provides functions to run a full simulaion
from either a dict with `run` or argv with `main`

Acts as executable if __name__ == '__main__'
parsing the parameters dictionary from argv

"""
import sys
from sim.core.parser import parser
import argcomplete

argcomplete.autocomplete(parser)

from sim.core.boot_exp import boot_exp


# * Main function

def run(args_dict,
        out_fn=sys.stdout.write,
        header=True):
    """Run a full simulation for parameters in args_dict.
    if not provided out_fn defaults to writing to stdout.
    The value of args_dict['R'] will be computed as c*T.

    Relies on run_batch after adding R to the dict, forawrding out_fn

    Use this function is importing the project as lib instead
    of main which reads args from argv

    """
    # print(args_dict)
    args_dict['R'] = args_dict['c'] * float(args_dict['T'])
    boot_exp (args_dict,out_fn=out_fn,header=header)

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


# Test the argumet parser
def test_0():
    args = parser.parse_args(["--m", "5",
                              "--T", "1000",
                              "--c", "0.1",
                              "--sim", "random",
                              "--stake_f", "eq",
                              "--times", "300"])
    return args
