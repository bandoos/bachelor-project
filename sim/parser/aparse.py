import argparse
import json
#from completers import *
#import cqrs

class StoreDictKeyPair(argparse.Action):
     def __init__(self, option_strings, dest, nargs=None, **kwargs):
         self._nargs = nargs
         super(StoreDictKeyPair, self).__init__(option_strings, dest,
                                                nargs=nargs, **kwargs)
     def __call__(self, parser, namespace, values, option_string=None):
         my_dict = {}
         for kv in values:
             k,v = kv.split("=")
             my_dict[k] = v
         setattr(namespace, self.dest, my_dict)

class StoreDictJSON(argparse.Action):
     def __init__(self, option_strings, dest, **kwargs):
         super(StoreDictJSON, self).__init__(option_strings, dest,
                                                 **kwargs)

     def __call__(self, parser, namespace, values, option_string=None):
         print ("!!!!!", values)
         my_dict = json.loads (values)
         setattr(namespace, self.dest, my_dict)

RAW = "opt-type/raw"

""" Grammar for schema is:

 S -> P // starts with a parser
 // parser has args (...) options and commands
 P -> { 'name': <string>, ..p , 'options': L, 'commands': T }
 // L is a list of options
 L -> [O*]
 O -> { ..o } // which are argparse args maps
 // commands are lists of parsers
 T -> [P*]

..p is any kv seq accepted by subparser creation
..o is any kv seq accepted by add_argument
"""

def Flag (name,hel,**kwargs):
    return {'name':name,
            'action':'store_true',
            'help':'(FLAG): '+hel,
            **kwargs}

def Opt (name,help,**kwargs):
    return {'name':name,
            'help':'(OPT): '+help,
            **kwargs}

def Cmd (name,conf={},options=[],commands=[]):
    return {'name':name,
            'conf':conf,
            'options':options,
            'commands':commands}


# For each subparser its 'name' is used
# to derive the destionationin lex env as follows:
subparser_cmd_dest = lambda x: x + "_cmd"


# In order to build the parser we recursively traverse
# the schema tree, with custom handlers for toplevel
# and an helper to build the args (which cannot recurse),
# recursing on subparsers
def build_args (api,parser,schema):
    for o in schema ['options']:
        name = o['name']
        del o ['name']
        parser.add_argument (name,**o)

def build_level(api,parser,schema):
    """Build the args for this level.
    Then if there are subparsers for this level, trigger their
    creation recursively

    """
    build_args(api,parser,schema)
    subcmds = schema.get('commands') or []
    # if no subparser should be built, then exit
    if len(subcmds) == 0:
        return
    # else recurse for all subparsers
    name = schema['name']
    sub_dest = subparser_cmd_dest(name)
    sub_conf = schema['conf']
    sub_conf['dest'] = sub_dest
    subps = parser.add_subparsers(**sub_conf)
    for subc in subcmds:
        subpars = subps.add_parser(
            subc['name'],
            **subc['conf'])
        build_level(api,subpars,subc)


def build_toplevel (prog_name,api,schema):
    parser = argparse.ArgumentParser (prog=prog_name,allow_abbrev=True)
    build_level(api,parser,schema)
    return parser



# parse some argument lists
#parser.parse_args(['a', '12'])


#parser.parse_args(['--foo', 'b', '--baz', 'Z'])
