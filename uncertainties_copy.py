import sympy as sym
import numpy as np
import pandas as pd
from math import floor, log10

def fexp(f):
    return int(floor(log10(abs(f)))) if f != 0 else 0

def fman(f):
    return f/10**fexp(f)

class Observable():
    def __init__(self, name, symbol='', value=0.0, uncertainty=0.0):
        self.name = name.capitalize()
        self.symbol = symbol # string
        self.value = value
        self.uncertainty = uncertainty
        
    def set_math_defintion(self, str_math_def):
        self.math_def = sym.sympify(str_math_def)
    
    def calc_value(self, variables_array):
        return self.math_def.subs(variables_array)
    
    def  calc_unc(self, variables_values, errors, constants={}, sign_fig=0):
        var_values = variables_values
        ## add constant values to the dataframe. Each value is repeated on each trial
        for constant_symbol, value in constants.items():
            var_values[constant_symbol] = [value for i in range(len(var_values))]
        
        mean_variable_values = variables_values.mean(axis=0)
        
        variables = [(index, value) for index, value in mean_variable_values.iteritems()]
        
        variables_plus_delta = [(index, value + errors[index]) for index, value in mean_variable_values.iteritems()]
        
        f = self.calc_value(variables)
        f_plus_delta = self.calc_value(variables_plus_delta)
        
        delta_f = abs(f_plus_delta - f) # the uncertainty of the observable is calculated as f(x + delta_x) - f(x)
        
        figures = abs(fexp(delta_f)) if sign_fig == 0 else sign_fig    
        
        self.value = round(f, figures)
        self.uncertainty = round(delta_f, figures)
           
    def cal_unc_direct_trials(self, trials_vals, error=0.0, sign_fig=0, combine_errors=False):
        val = trials_vals.mean() # reported value is the average of values
        uncr = trials_vals.sem() if combine_errors is False else (trials_vals.sem()**2 + error**2)**(1/2) # reported uncertainty is the squared mean of uncertainties
        figures = abs(fexp(uncr)) if sign_fig == 0 else sign_fig 
        self.value = round(val, figures)
        self.uncertainty = round(uncr, figures)
          
    def independent_trials(self, variables_values: pd.DataFrame, errors: pd.Series, constants={},sign_fig=0):
        independent_trials = pd.DataFrame({'val' : [], 'uncertainty' : []}) 
        
        var_values = variables_values.copy()
        ## add constant values to the dataframe. Each value is repeated on each trial
        for constant_symbol, value in constants.items():
            var_values[constant_symbol] = [value for i in range(len(var_values))]
                
        for i in range(len(variables_values)):
            variables = [(index, value) for index, value in variables_values.iloc[i].iteritems()] # read each row of dataframe of values. Each row is a series containig variables measured on a single trial
            variables_plus_delta = [(index, value + errors[index]) for index, value in variables_values.iloc[i].iteritems()] # to each value is added the correspondent incertainty
            
            f_plus_delta = self.calc_value(variables_plus_delta)
            f = self.calc_value(variables)
            
            delta_f = abs(f_plus_delta - f) # the uncertainty of the observable is calculated as f(x + delta_x) - f(x)

            # format to proper number of significant figures
            figures = abs(fexp(delta_f)) 
            delta_f = round(delta_f, figures)
            f = round(f, figures)
            independent_trials.loc[i] = [f, delta_f]
        self.independent_trials = independent_trials # store calculated values for each trial
        
        # average indirect trials
        vals = self.independent_trials['val']
        val = vals.mean() # reported value is the average of values
        uncrts = self.independent_trials['uncertainty']
        uncr = (np.array([err**2/len(uncrts) for err in uncrts]).sum())**(1/2) # reported uncertainty is the squared mean of uncertainties
        figures = abs(fexp(uncr)) if sign_fig == 0 else sign_fig
        self.value = round(val, figures)
        self.uncertainty = round(uncr, figures)
       
    def pack_as_tuple(self):
        return tuple([self.symbol, self.value, self.uncertainty])
    
    def __str__(self):
        report = self.name + '\n' + str(self.value) + ' +/- ' + str(self.uncertainty)
        return report
    
    def __repr__(self):
        report = str(self.value) + ' +/- ' + str(self.uncertainty) 
        return report