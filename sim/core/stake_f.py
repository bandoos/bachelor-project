
# import decorator
import scipy.stats as st
from matplotlib import pyplot as plt

eq_stake_f = lambda _,n: st.uniform.rvs(size=1,loc=1/n,scale=0)[0]

#gamma_stake_f_1 = lambda _,__ : st.gamma.rvs(size=1,a=1)[0]

#quad_stake_f = lambda i,_ : (i+1)**2 # quadratic

pareto_stake_f = lambda _,n: st.pareto.rvs(b=1.16)

beta_stake_f = lambda _,n: st.beta.rvs(2,2)


# in order to display and persist functions used,
# we map the function pointers to strings
stake_f_map = {
    eq_stake_f:"eq",
    #gamma_stake_f_1:'gamma_1',
    #quad_stake_f:'quad_1',
    pareto_stake_f:'pareto',
    beta_stake_f:'beta'
}

stake_f_label_to_fn = {
    "eq":eq_stake_f,
    #'gamma_1':gamma_stake_f_1,
    #'quad_1':quad_stake_f,
    'pareto':pareto_stake_f,
    'beta':beta_stake_f
}

### END ###
