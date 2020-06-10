from pprint import pprint

class UCommand ():
    """This class provides:
    - a single field: meta_key
    - a single method: invoke
    - an implementation for __call__ with one argument, that simply
    dispatches `invoke' with that arg

    The abstaction here is the following:

    The `invoke' method accpets a lexical `env' dictionary, the
    `meta_key' field is used to access the env. The resulting value,
    which should be a string, is used to pick a method among those of
    the UCommand extension instance. That method is then dispatched
    passing the env.

    """

    def __init__(self,meta_key):
        self.meta_key = meta_key

    def invoke(self, env):
        """Use self.meta_key to get from env the name of the method to
        invoke. Evaluate the method call catching and reporting any
        exceptions

        """
        try:
            key = env.get(self.meta_key)
            #print("INVOKE '{}' on {}".format(key, type(self)))
            f = getattr(self,key) # f is a bound method
                                  # (i.e. partialed with self)
            return f(env)
        except Exception as e:
            #print("An error occured during api invokation!")
            pprint(e)

    def __call__(self,env):
        return self.invoke(env)


def subcmd(ext_class):
    """Delegate the wrapped method to a temporary
    instance of ext_class. The wrapped function should accept
    (self, env)

    """
    def cmd_decorator(func):
        def func_wrapper(self,env):
            o = ext_class()
            return o(env)
        return func_wrapper
    return cmd_decorator
