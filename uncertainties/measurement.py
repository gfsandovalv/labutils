import sympy as sym
from sympy.parsing.sympy_parser import parse_expr
from pandas import DataFrame, Series
from numpy import mean, array
from math import sqrt

class Observable:
    def __init__(self, symbol='', definition='', data=None, last_row_error=False) -> None:
        """_summary_

        Args:
            symbol (str, optional): Math symbol of the observable. Defaults to ''.
            definition (str, optional): Math definition of symbol: RHS of symbol equality. The string is converted to a sympy expression. Defaults to ''.
            data (_type_, optional): Table of data in which each row represents a take of measurement. Defaults to None.
            last_row_error (bool, optional): Indicates whether the data table is passed with the last row containing error of each variable. Defaults to False.
        """        
        self.symbol = symbol
        self.definition = parse_expr(definition)
        self.takes_errors = None
        self.error = None   
        
        if type(data) is not type(None):
            df = DataFrame(columns=[sym.name for sym in self.definition.free_symbols])
            df[df.columns] = data[df.columns]
            self.data = df
            values = [self.definition.subs(self.data.iloc[i].items()) for i in range(len(self.data))]
            self.values = values
            self.mean_value = mean(values)
        else:
            self.data = data
            self.values = values
        
        if last_row_error is True:
            self.vars_errors = self.data.iloc[-1]
            self.data.drop(data.tail(1).index, inplace=True)
            #self.data.rename(index={len(data) - 1:'error'}, inplace=True)
    
    def calc_error(self, method='deltas'):
        if method == 'deltas':     
            takes_errors = []
            for take in range(len(self.data)):
                take_value = self.definition.subs(self.data.iloc[take].items())
                alpha_args = {}
                for symbol in self.data.columns:
                    alpha_args[symbol] = self.data.iloc[take].copy()
                    alpha_args[symbol].loc[symbol] = alpha_args[symbol].loc[symbol] + self.vars_errors.loc[symbol]
                partial_sq_errors = array([abs(self.definition.subs(arg[1].items()) - take_value)**2 for arg in alpha_args.items()])
                take_error = sqrt(partial_sq_errors.sum())
                takes_errors.append(take_error)
            self.takes_errors = Series(data=takes_errors)
            self.takes_errors.index += 1
            self.error = self.takes_errors.mean()
            
        elif method == 'derivatives':
            partial_derivatives = {var.name : sym.diff(self.definition, var) for var in self.definition.free_symbols}
            takes_errors = Series({take + 1 : sym.sqrt(array([(partial_derivatives[var.name].subs(self.data.iloc[take].items())**2)*self.vars_errors[var.name]**2 for var in self.definition.free_symbols]).sum()) for take in range(len(self.data))}) 
            self.takes_errors = takes_errors
            self.error = self.takes_errors.mean()         
    