#!/usr/bin/python3
# PYTHON_ARGCOMPLETE_OK

# * Demo
import argcomplete

from sim.executor.db.parser import mk_parser
from sim.executor.db.fs import CMDDriver
from sim.executor.dbdriver import GRIDFS_DB

fsd = CMDDriver()
parser = mk_parser(fsd)

argcomplete.autocomplete(parser)


from sim.executor.db.logger  import logger
from pprint import pprint


#fsd.ls()

#fsd({'fs-cmd':'ls'})

def run(args):
    logger.debug(args)
    if args.get('dry'):
        pprint(args)
    else:
        r = fsd(args)
        logger.debug(f"return={r}")

#run({'fs-cmd':'ls'})


def main ():
    args = vars(parser.parse_args())
    run(args)


if __name__ == '__main__':
    logger.debug("MAIN startup...")
    main()
