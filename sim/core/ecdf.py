# ecdf.py
import numpy as np
from scipy import interp
def ecdf(data):
    """credits: https://www.codementor.io/kripanshubharga/calculate-ecdf-in-python-gycltzxi3"""
    data = np.array(data)
    # create a sorted series of unique data
    cdfx = np.sort(np.unique(data))
    # x-data for the ECDF: evenly spaced sequence of the uniques
    x_values = np.linspace(start=min(cdfx), stop=max(cdfx),num=len(cdfx))

    # size of the x_values
    size_data = len(data)
    # y-data for the ECDF:
    y_values = []
    for i in x_values:
        # all the values in raw data less than the ith value in x_values
        temp = data[data <= i]
        # fraction of that value with respect to the size of the x_values
        value = temp.size / size_data
        # pushing the value in the y_values
        y_values.append(value)
    # return both x and y values    
    return x_values,y_values

# Use a linear interpolator to make python function out of it.
def make_interp(xs,ys):
    def f(x):
        nonlocal xs, ys
        return interp(x,xs,ys)
    return np.vectorize(f)