"""
Executor tasks module
=====================

Defines celery tasks required for the experiment:

- run_exp_v2
- post_proc_batch_v2

Implements a custom task appender ``extending sim.executor.dbdriver``.


"""

from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
# import cgroups
# import subprocess
import pymongo
import celery as cel
#import functools as fp
import itertools as it

# local imports
from sim.executor.dbdriver import TaskAppender, CsvAggregator, ExpTaskAppender

# Build the celery application
app = Celery('sim-stake-executor')
app.config_from_object('sim.executor.celeryconf')


# * Exception types

JOB_OK=0
def exception_as_dict(ex):
    try:
        return dict(type=ex.__class__.__name__,
                    errno=ex.errno, message=ex.message,
                    strerror=exception_as_dict(ex.strerror)
                    if isinstance(ex.strerror,Exception) else ex.strerror)
    except Exception:
        return dict(err=str(ex))


class HeaderMismatchError(Exception):
    pass

class ZeroSuccessfullJobsError(Exception):
    pass

class MissingJobIdError(Exception):
    pass


def with_job_id(ctx,task_id):
    """
    Ensures an exception is thrown if
    task_id is None. The exception will
    include the ctx object passed.
    """
    if task_id is None:
        raise MissingJobIdError(ctx)
    return task_id


class _Job_id():
    """Context manager for job id.
    Ensures the given req has a id member.  When called raising
    MissingJobIdError otherwise.

    """
    def __init__(self,ctx,req):
        self.ctx = ctx
        self.req = req

    def __call__(self):
        if self.req.id is None:
            raise MissingJobIdError(self.ctx)
        return self.req.id

    def __enter__(self):
        return self

    def __exit__(self,*args):
        pass

## Todo define a base class for the callable task
# such that try except logic is abstracted this should also make the
# task autodocumented

@cel.task(bind=True) # register the task on app
def run_exp_v2(self,args_dict,
                    batch_uuid,
                    handle_all=True,
                    buff_size=10):
    """Task to run an experiment via ``sim.core.main.run(args_dict,...)``.

    Requies batch_uuid to be passed in.

    Derives the job id from the celery request.id

    Builds task appender for the job buffering size of 10 records by
    default. User ``buff_size`` kwarg to customize logging if you want
    to hit the database at higher/loewer rate.

    Catches all exceptions if ``handle_all`` kwarg is not specified to be False

    The job may be revoked cleanly via celery and it will return a document
    with job-exit=-1

    NOTE: results of the job do not include the actual output
    of the simulator, only task metadata. that is directly saved to the database
    via the ExpTaskAppender.

    """
    try:
        # import the simulator dynamically
        import sim.core.main as m
        # Establish job context
        with _Job_id(self,run_exp_v2.request) as idfn:
            job_id = idfn()
            base = {'job_args':args_dict,
                    'batch_uuid':batch_uuid,
                    'job_id': job_id}

            # Establish appender context
            with ExpTaskAppender(job_id, # init db client &  the appender
                                batch_id=batch_uuid,
                                buff_size=buff_size) \
                                as appender:

                m.run(args_dict,appender) # run experiment with stateful appender

                return  {**base,
                        'job-exit': JOB_OK}


    except SoftTimeLimitExceeded as e:
        return {**base,
                'job-state': 'revoked',
                'job-exit': -1}

    except Exception as e:
        if handle_all:
            return {**base,
                    'job-state': 'fault',
                    'job-exit': 1,
                    'exception': exception_as_dict(e)}
        else:
            raise e




@cel.task(bind=True)
def post_proc_batch_v2(self,batch_uuid):
    try:
        base = {'batch_uuid':batch_uuid,
                'stage': 'post_proc_batch_v2'}

        with CsvAggregator(batch_uuid) as agg:
            base['aggregator-output'] = str(agg())

        return {**base, 'job-exit':0}

    except SoftTimeLimitExceeded as e:
        return {**base,
                'job-state': 'revoked',
                'job-exit': -1}
