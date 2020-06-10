#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK

"""
sim.executor.launcher
=====================

provides cli to dispatch experiment batches.

An Experiment definition is any module that
exports a ``batch`` member. ``batch`` should
be a callable that returns a list of dictionaries
being the arguments for each simulaion in the batch.


Default experiments are defined in sim.executor.experiments
using the ``executor.batch.ibatch`` semantics.
Note though that any python module in the $PYTHONPATH
exporting a valid ``batch`` callable is good to go.

The name of the module shoudl be provided as
'--exp-module' from cli and as 'exp_module' if using
programmatically via run() instead of main()


When running from cli passing the '--async' flag will
not force the program to wait for post_processing completion
on the batch. Instead it will print metadata to stdout.


"""

## Corner case, if some job in the batch fails before
# producing any output it will not raise an AggregationError
# when postprocessing
# this is be solved by a message with serial_n -1
# that registers in the output log that job before invoking it

## Note
# there should be a separate high-prio queue for handling post_proc
# tasks and ensure their result is not starved by new batches


# ** Args parser
import argparse
import argcomplete
import IPython
from sim.executor.logger import logger

parser = argparse.ArgumentParser('sim-launcher')
parser.add_argument('--exp-module',
                    type=str,
                    default='sim.executor.experiments.exp_365').completer = \
                        IPython.core.completer.Completer()

parser.add_argument('--async','-a',action='store_true')

argcomplete.autocomplete(parser)

## Main imports
import uuid
from celery import group
from celery.result import AsyncResult


from importlib import import_module
import sys
from pprint import pprint


## * DEVEL import environ vars
##----------------------------------------##
if not __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path  # Python 3.6+ only
    load_dotenv(Path('/home/bandoos/repos/sim-core-0.1/compose/vars.env'))
##----------------------------------------##

from sim.executor.tasks import run_exp_v2, post_proc_batch_v2



## ** Utils

def batch_sign(result,batch_uuid):
    result._batch_uuid = batch_uuid

class NotCallableError(Exception):
    pass


## ======================================
## ** Core logic
def run_and_agg_v2(batch_fn):
    """Expand the given batch, generate uuid for the batch,
    then dispatch a group of tasks to the main queue, and a callaback
    to process all results after.
    uses``sim.executor.tasks.run_exp_v2`` to run the experiment and
    ``sim.executor.task.post_proc_batch_v2`` for the post-processing

    """
    batch_uuid = uuid.uuid4()
    batch = batch_fn()
    # define task workflow:
    # do work in parallel
    task = group(run_exp_v2.s(d,batch_uuid) for d in batch) \
        | post_proc_batch_v2.si(batch_uuid) # then serial postprocessing
    dispatch = task()
    batch_sign(dispatch,batch_uuid)
    return dispatch



def run_and_agg_v2_from_conf(module_name):
    """Same as run_and_agg_v2 but loads the batch_fn
    from a module, dynamically imported.
    The batch_fn should be a memeber of the loaded module
    named ``batch``.
    """
    logger.info(f"Importing {module_name}")
    module = import_module(module_name)
    logger.info(f"Verifying {module_name}.batch")
    batch_fn = module.batch
    if not callable(batch_fn):
        raise NotCallableError(batch_fn)
    logger.info(f"Imported and verified {module_name}.batch")
    return run_and_agg_v2(batch_fn)



## ======================================
## ** IO logic

def run(args_dict):
    """Dispatch a batch from args_dict.

    args_dict should countain the 'exp_module' key with value a string
    pointing to an importable module

    """
    try:
        module_name= args_dict['exp_module']
        return run_and_agg_v2_from_conf(module_name)

    except AttributeError:
        logger.error(f"{module_name}.batch does not exists!\n"
                     f"check that ``batch`` is declared in the file!")

        sys.exit(1)

    except ModuleNotFoundError:
        logger.error(f"{module_name}.batch does not exists!\n"
                     f"check the spelling, or check that {module_name} is "
                     "in the PYTHONPATH")
        sys.exit(2)

    except NotCallableError:
        logger.error(f"{module_name}.batch is not expandable!\n"
                     f"check that {module_name}.batch is either callable")
        sys.exit(3)


def main():
    args = parser.parse_args().__dict__
    #pprint(args)
    dispatch = run(args)
    logger.info(f"Dispatched batch: {dispatch._batch_uuid}")
    if not args['async']:
        logger.info(f"Blocking on completion of {dispatch._batch_uuid}")
        pprint(dispatch.get())
        return
    pprint(dispatch.__dict__)


if __name__ == "__main__":
    main()



# * thinkering


# r = run_and_agg_v2_from_conf('sim.executor.experiments.exp_365')
# from pprint import pprint

# for i in r.collect():
#     result = i[0]
#     pprint(result.__dict__)
#     parent = result.parent
#     for j in parent.results:
#         # r = AsyncResult(j)
#         print(j.__dict__)
