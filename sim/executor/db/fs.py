import os
import gridfs

from sim.executor.db.logger import logger

if  __name__ == "__main__":
    from dotenv import load_dotenv
    from pathlib import Path  # Python 3.6+ only
    load_dotenv(Path('/home/bandoos/repos/sim-core-0.1/compose/vars.env'))

os.environ

import sim.executor.dbdriver as dbd
from sim.executor.dbdriver import GRIDFS_DB

# * Dbdriver for gridfs

# Main logic
# ==========================================

class IFSDriver(dbd.DBDriver):
    def __init__(self,fs_db_name):
        super().__init__()
        self.fs_db_name = fs_db_name
        self.gfs = gridfs.GridFS(self.c[self.fs_db_name])








# CLI application
# ==========================================

# * Singleton base driver
import sys

from sim.cmd.ucmd import UCommand, subcmd

class FSDriver(UCommand,IFSDriver):
    """
    Singleton manager for the IFSDriver in the cli client application
    """
    INSTANCE = None
    def __init__(self):
        if FSDriver.INSTANCE is None:
            UCommand.__init__(self,'toplevel_cmd')
            IFSDriver.__init__(self,GRIDFS_DB)
            FSDriver.INSTANCE = self
        else:
            return FSDriver.INSTANCE

# * Commands relying on the signleton

class ECommand (UCommand):
    META_KEY=None
    def __init__ (self,*a,**k):
        super ().__init__ (type(self).META_KEY,*a,**k)
        self.driver = FSDriver.INSTANCE


# ** Fs

class EFs(ECommand):
    META_KEY="fs_cmd"

    def _ls(self,env={}):
        return self.driver.gfs.list()

    def ls(self,env={}):
        for line in self._ls(env):
            print(line)

    def _get(self,env):
        target = env['filename']
        gridout = self.driver.gfs.get_last_version(target)
        logger.debug(f"{target}, CHUNK_SIZE={gridout.chunk_size}, LEN={gridout.length}, MD5={gridout.md5}")
        return gridout

    def get(self,env):
        for chunk in self._get(env):
            sys.stdout.buffer.write(chunk)

# ** Toplevel command

class CMDDriver(FSDriver):
    def __init__(self):
        FSDriver.__init__(self)

    @subcmd(EFs)
    def fs(self,env):
        pass
