import pymongo
import sys
import tempfile as tmp
from abc import ABC
import abc
import pprint
import pprint as pp

import sim.executor.celeryconf as conf

class Client(pymongo.MongoClient):
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

This can be persisted by creating the record on the first
invokation and append to some field on later invokations.

It could buffer updates if the output is produced at a rate
not suitable for db updates



"""


TASK_DB = "from_celery"
GRIDFS_DB = "executor-gridfs"

class TaskDBDriver(object):
    def __init__(self):
        self.c = Client()
        self.db = self.c[TASK_DB]
        self.state = {'phase':None}

    # as Context manager
    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        self.c.close()

    def __repr__(self):
        return f'<{type(self)}: {pp.pformat(self.__dict__)}>'


class TaskAppender(TaskDBDriver):
    def __init__(self,batch_id, buff_size=1):
        super().__init__()
        self.batch_id = batch_id
        self.coll = self.db[str(batch_id)]
        self.buff_size = buff_size
        self.buff = []


    def _flush(self):
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
        return self._append(args)


    def __exit__(self,*exc_args):
        self._flush()
        return super(TaskAppender,self).__exit__(*exc_args)

from bson.son import SON
from collections import OrderedDict

CELERY_TASKMETA='celery_taskmeta'


# * Default aggregation pipeline
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

# pprint.pprint (list ( coll.aggregate (p)))

class AggregationError(Exception):
    pass

class TaskAggregator(TaskDBDriver):
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

import gridfs
import os

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



# * combing context managers




"""
class A():
    def __enter__(self):
        print("enter A")
        return self

    def __exit__(self,*args):
        print("exit A")

class B(A):

    def __call__(self):
        raise Exception('ti')

    def __enter__(self):
        super(B,self).__enter__()
        print("enter B")
        return self

    def __exit__(self,*args):
        print("exit B")
        return super(B,self).__exit__(*args)



b = B()



with b as ctx:
##    ctx()
    print("mona")

"""
