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
import os
# import cgroups
# import subprocess
import pymongo
import celery as cel
import functools as fp
import itertools as it

# local imports
from sim.executor.dbdriver import TaskAppender, CsvAggregator
from sim.executor.logger import logger
import sim.core.main as m

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

# * Extend the DB task appender

class ExpTaskAppender(TaskAppender):
    """Task appender for the main experiment.
    Being an extension of TaskAppender means Required `*args` include:

    - batch_id

    Optional kwargs include

    - buff_size=1


    Will log documents to a mongodb collection named as
    the value of batch_id in the database
    ``sim.executor.dbdriver.TASK_DB``

    """
    def __init__(self,job_id,*args,**kw):
        super().__init__(*args,**kw)
        self.serial_n = -1 # this implem uses 1 meta doc (i.e. negative serial)
        self.job_id = job_id
        self({'event':'appender-setup'}) # <- setup meta doc

    def _serial_sign(self,x):
        d = x if isinstance(x,dict) else {'payload':x}
        d['serial_n'] = self.serial_n
        d['job_id'] = self.job_id
        self.serial_n += 1
        return d

    def __call__(self,*args):
        return self._append(map(self._serial_sign, args))

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
    """ Context manager for job id
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
