import sympy as sym
import pandas as pd
import numpy as np
from math import floor, log10

def fexp(f):
    return int(floor(log10(abs(f)))) if f != 0 else 0

def fman(f):
    return f/10**fexp(f)


class Observable():
    def __init__(self, parameters_table, str_math_def):
        self.parameters = pd.read_csv(parameters_table).set_index('symbol')
        self.math_def = sym.sympify(str_math_def)
        self.mean_value = self.math_def.subs(self.parameters['val'].items())
        
        mean_vals = self.parameters['val'].copy()
        uncertainties_val = self.parameters['delta']
        alpha_args = {}
        for symbol in self.parameters.index:
            alpha_args[symbol] = mean_vals.copy()
            alpha_args[symbol].loc[symbol] = mean_vals.loc[symbol] + uncertainties_val.loc[symbol]
        
        partial_sq_errors = np.array([abs(self.math_def.subs(variable.items()) - self.mean_value)**2 for variable in alpha_args.values()])
        self.total_error = partial_sq_errors.sum()
    
    def __str__(self):
        return str(self.mean_value) + ' +/- ' + str(self.total_error) 

