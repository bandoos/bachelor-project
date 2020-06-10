from sim.parser.aparse import *

class ChoicesCompleter(object):
    def __init__(self, api, fn):
        self.api = api
        self.fn = fn

    def __call__(self, **kwargs):
        try:
            return self.fn(self.api)
        except Exception as e:
            return []


def build_schema(driver):
    complete_files = ChoicesCompleter(driver,
                                      lambda d: d({'toplevel_cmd':'fs',
                                              'fs_cmd':'_ls'}))


    return Cmd('toplevel',{},
               commands=
               [Cmd('fs',{},
                    commands=
                    [Cmd('ls',{}),
                     Cmd('get',{},
                         options=
                         [Opt('filename','name of the file to retrieve',
                              choices=complete_files())])])])

def mk_parser(driver):
    return build_toplevel("dctl",driver,build_schema(driver))
