# ** Reward functions

def r_const(params):
    return params['R']/params['T']

# define geometric reward function:

def r_g(params):
    """Geometric reward function.

    accepts a dictionary specifying required
    parameters, and 't'.

    Suitable params dictionary is obtained by invoking .params() on a
    simulaion instance

    (1+R)^(t/T) - (1+R)^((t-1)/T)

    """
    return (1+params['R'])**(params['t']/params['T'])\
                    - (1+params['R'])**((params['t']-1)/params['T'])


rew_fn_mappings = {
    r_const: 'r_const',
    r_g: 'r_g'
}
