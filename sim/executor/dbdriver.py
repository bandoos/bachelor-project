"""
dbriver (database interface module)
===================================

Defines the base classes used to define
database drivers.

Includes a general ``TaskDBDriver`` class
plus ``TaskAppender`` for output collection
and ``TaskAggregator`` for output postprocessing.

A csv-based implementation of ``TaskAggregator`` is defined.

TODO move the corresponding appender ``ExpTaskAppender`` from
tasks to here. Also dbdriver could be a module

The classes defined in this module should be used as context managers
in a `with` statement to ensure resources are released, especially in long
running jobs

"""
import pymongo
import sys
import gridfs
import os
import tempfile as tmp
from abc import ABC
import abc
import pprint as pp
from bson.son import SON

import sim.executor.celeryconf as conf

class Client(pymongo.MongoClient):
    """Extends the pymongo client
    to setup from config files
    """
    def __init__(self):
        super().__init__(conf.result_backend)

"""
c = Client()

db = c['from_celery']

db['celery_taskmeta'].find_one()

coll = db['mona']
coll.insert_one({'mona':"ti"})


c.close()

"""


"""
the idea is to pass to the task an out_fn
that produces records to a collection named
after the batch id. The function can be stateful if
needed by closuring or using callables.

For example for sim-core-0.1 the first invokation
produces an header, the remaning ones produce rows.

It can buffer updates if the output is produced at a rate not suitable
for db updates



"""


class DBDriver(object):
    """Database client wrapper that can be used as context in a `with`
    statement.  When the context is exited the db connection resources
    are released.

    """
    def __init__(self):
        self.c = Client()

    # as Context manager
    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        self.c.close()

    def __repr__(self):
        return f'<{type(self)}: {pp.pformat(self.__dict__)}>'

    # def __getattribute__(self,x):
    #     return self.c[x]




TASK_DB = os.environ.get('EXECUTOR_DB') or "from_celery"
GRIDFS_DB = os.environ.get('EXECUTOR_GRIDFS') or "executor-gridfs"
CELERY_TASKMETA='celery_taskmeta'

class TaskDBDriver(DBDriver):
    """Database client wrapper that can be used as context in a `with`
    statement.  When the context is exited the db connection resources
    are released.

    """
    def __init__(self):
        super().__init__()
        self.db = self.c[TASK_DB]
        self.state = {'phase':None}


# * Output stages

class TaskAppender(TaskDBDriver):
    """Base appender that flushes to
    a colletion named like batch_id in the
    ``TASK_DB`` database.

    If `buff_size` is specified at constructor level
    then that will be the size of the docuement buffer before
    flushing. This is the number of documents, not their size in bytes.
    Buffering defaults to 1 i.e. no buffering

    Toplevel usage should only use this objects as callables, under a
    `with` statement context, ensuring db resources are released and
    the buffer is flushed.

    """
    def __init__(self,batch_id, buff_size=1):
        super().__init__()
        self.batch_id = batch_id
        self.coll = self.db[str(batch_id)]
        self.buff_size = buff_size
        self.buff = []


    def _flush(self):
        """Flush contents of the buffer to the database"""
        if len(self.buff) > 0:
            r =  self.coll.insert_many(self.buff)
            self.buff = []
            return r

    def _append(self,docs):
        self.buff.extend(docs)
        if  len(self.buff) < self.buff_size:
            return None
        return self._flush()

    def __call__(self,*args):
        """Using the object as callable will trigger an ``_append``
        Which will flush if buffering size was reached."""
        return self._append(args)


    def __exit__(self,*exc_args):
        self._flush()
        return super(TaskAppender,self).__exit__(*exc_args)


# ** Basic Extension

class ExpTaskAppender(TaskAppender):
    """Task appender for the main experiment.
    Being an extension of TaskAppender means Required `*args` include:

    - batch_id

    Optional kwargs include

    - buff_size=1


    Will log documents to a mongodb collection named as
    the value of batch_id in the database
    ``sim.executor.dbdriver.TASK_DB``

    Keeps track of the serial number of the output record.  Produces a
    meta record (i.e. serial_n = -1) to notify the setup of the
    appender.

    Records produced by this appender are
    {'payload':<any>, 'serial_n':<int>, 'job_id':<uuid-str>}

    """
    def __init__(self,job_id,*args,**kw):
        super().__init__(*args,**kw)
        self.serial_n = -1 # this implem uses 1 meta doc (i.e. negative serial)
        self.job_id = job_id
        self({'event':'appender-setup'}) # <- setup meta doc
        self._flush() # <- force the meta write

    def _serial_sign(self,x):
        d = {'payload':x}
        d['serial_n'] = self.serial_n
        d['job_id'] = self.job_id
        self.serial_n += 1
        return d

    def __call__(self,*args):
        return self._append(map(self._serial_sign, args))

# * Aggregation stages

# ** Default aggregation pipeline
# joins with the celery_taskmeta to
# attach task metadata to output documents

def mk_agg_pipeline(lookup_coll=CELERY_TASKMETA):
    pipeline = [{'$sort': SON([('job_id',pymongo.ASCENDING),
                               ('serial_n',pymongo.ASCENDING)])},
                {'$lookup':
                 {'from':lookup_coll,
                  'localField': 'job_id',
                  'foreignField': '_id',
                  'as':'job_meta'}},
                {'$project':
                 {'payload': 1,
                  'serial_n':1,
                  'job_id':1,
                  'job_meta': {'$arrayElemAt': ['$job_meta',0]}}}]
    return pipeline


# c = Client()
# coll = c.from_celery ['d59beb0d-90a6-491f-b3db-c58f188d99c4']
# p = mk_agg_pipeline ()


class AggregationError(Exception):
    pass

class TaskAggregator(TaskDBDriver):
    """Basic aggregator.

    the ``kernel`` method should be overriden by subclasses
    to implement domain specific logic.

    Toplevel usage should use these objects as callables,
    passing arguments required by the specific kernel.

    Note that since this is TaskDBDriver extension it should
    be used in a `with` context to ensure resource cleanup.

    """
    # state:
    # batch_id : str
    # cursor : Maybe <pymongo Cursor>

    def __init__(self,batch_id):
        super().__init__()
        self.batch_id = str (batch_id)
        self.cursor = None


    def _mk_pipeline(self):
        return mk_agg_pipeline ()

    def _all_docs_cursor(self,refresh=False):
        """caches the cursor, pass refresh=True to force creation of a new
        cursor

        """
        if self.cursor is None or refresh:
            self.cursor = self.db[self.batch_id] \
                              .aggregate (self._mk_pipeline ())
        return self.cursor

    @abc.abstractmethod
    def kernel(self,doc,*args,**kw):
        pass

    def finalize(self):
        pass

    def _check_doc_sanity (self,doc):
        if doc ['job_meta'] ['status'] == "SUCCESS" and \
           doc ['job_meta'] ['result'] ['job-exit'] == 0:
            return True
        else:
            raise AggregationError ('Invalid document, some job has failed!',
                                    {'faulty-doc':doc})

    def __call__(self,*args,**kw):
        for doc in self._all_docs_cursor():
            self._check_doc_sanity (doc)
            self.kernel(doc,*args,**kw)
        return self.finalize()


    def __exit__(self,*exc_args):
        self.cursor and self.cursor.close()
        super(TaskAggregator,self).__exit__(*exc_args)



class TaskResPrinter(TaskAggregator):
    """Trivial task aggregator that prints documents
    """
    def kernel(self,doc):
        print(doc)

"""

tagg = TaskResPrinter("efb24fa2-dd72-4147-89db-2cd6ec2e8d52")

tagg()

"""


class HeaderMismatchError(Exception):
    pass


class CsvAggregator(TaskAggregator):
    """A stateful aggregator that merges csv formatted
    output from documents in the database, ensuring header
    consistency. Reports an HeaderMismatchError if some
    document doesn not match with the current header.

    Processed Documents should bear 'job-id' and 'serial_n'
    as per default of TaskAggregator.
    Documents with 'serial_n' are expected to be headers.

    Once the first document is read the header is cached and
    checked for equality on successive headers.

    The documents should have their csv rows as strings under
    the 'payload' key

    """
    def __init__(self, batch_id,out_fn=None):
        """

        """
        super().__init__(batch_id)
        self.header = None
        self.out_fn = out_fn
        self.tmp_dir = tmp.mkdtemp() # move this to file based implem
        self.filename = batch_id + '.csv'
        self.tmp_path = self.tmp_dir + '/' + self.filename
        self.fptr = open(self.tmp_path, 'w')
        self.out_fn = out_fn or self.fptr.write
        self.gfs = gridfs.GridFS(self.c[GRIDFS_DB])


    #def _upload_file(self):

    def __exit__(self,et,ev,tb):
        print("Closing csv file: ", self.tmp_path)
        self.fptr.close()
        os.remove(self.tmp_path)
        print("Removing csv file: ", self.tmp_path)
        #os.rmdir(self.tmp_dir)
        super(CsvAggregator,self).__exit__(et,ev,tb)


    def _handler_header(self,doc):
        h = doc['payload']
        if self.header is None:
            self.header = h
            self.out_fn(h)
        elif self.header != h:
                raise HeaderMismatchError(self,header,h)
        else:
            pass # if header mathces skip the header

    def kernel(self,doc):
        # the negative serial documents are meta document so
        # the kernel does not need to process it.
        # sanity will still be checked by super
        if doc ['serial_n'] < 0:
            return None
        if doc ['serial_n'] == 0:
            return self._handler_header(doc)
        else:
            return self.out_fn(doc['payload'])

    def finalize(self):
        self.fptr.close()
        with open(self.tmp_path,'rb') as fptr:
            # upload the tmp file to gridfs
            fileid= self.gfs.put(fptr,filename=self.filename)
            print (f"Successfully loaded {self.filename} to GridFS")
            return fileid



# with CsvAggregator("efb24fa2-dd72-4147-89db-2cd6ec2e8d52") as agg:
#     agg()

#csvagg()
