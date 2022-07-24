from sympy import Symbol, latex, diff
from sympy.parsing.sympy_parser import parse_expr
from pandas import DataFrame, Series
from numpy import mean, array
from math import sqrt
from pylatex import Document, Section, Command, Math
from pylatex.utils import NoEscape

class Observable:
    def __init__(self, symbol='', definition='', data=None, last_row_error=False, value=0.0, error=0.0) -> None:
        """_summary_

        Args:
            symbol (str, optional): Math symbol of the observable. Defaults to ''.
            definition (str, optional): Math definition of symbol: RHS of symbol equality. The string is converted to a sympy expression. Defaults to ''.
            data (_type_, optional): Table of data in which each row represents a take of measurement. Defaults to None.
            last_row_error (bool, optional): Indicates whether the data table is passed with the last row containing error of each variable. Defaults to False.
        """        
        self.symbol = Symbol(symbol)
        if definition != '':
            self.definition = parse_expr(definition)
        else:
            self.definition = definition
        self.value = value
        self.error = error
        
        self.takes_errors = None
        self.values = None

       
        if type(data) is not type(None):
            df = DataFrame(columns=[sym.name for sym in self.definition.free_symbols])
            df[df.columns] = data[df.columns]
            self.data = df
        else:
            self.data = data

        if last_row_error is True:
            self.vars_errors = self.data.iloc[-1]
            self.data.drop(data.tail(1).index, inplace=True)
            
    def calc_values(self):
        values = array([self.definition.subs(self.data.iloc[i].items()) for i in range(len(self.data))])
        self.values = values
        self.value = mean(values)
                
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
            partial_derivatives = {var.name : diff(self.definition, var) for var in self.definition.free_symbols}
            takes_errors = Series({take + 1 : sqrt(array([(partial_derivatives[var.name].subs(self.data.iloc[take].items())**2)*self.vars_errors[var.name]**2 for var in self.definition.free_symbols]).sum()) for take in range(len(self.data))}) 
            self.takes_errors = takes_errors
            self.error = self.takes_errors.mean()
    
    def __str__(self):
        return str(self.value) + ' +/- ' + str(self.error)
        
    def __repr__(self) -> str:
        return str(self.symbol) + ' = ' + str(self.value) + ' +/- ' + str(self.error)
    
    def report(self, return_tex=True, generate_pdf=False):
        function_vars = latex(self.symbol) + ' = ' + latex(self.symbol) + latex(tuple(self.definition.free_symbols))
        expression = latex(self.symbol) + ' = ' + latex(self.definition)
        data = self.data.copy(deep=True)

        data[self.symbol.name] = self.values
        data.columns = ['$' + var_name + '$' for var_name in data.columns]
        data.index += 1
        data = data.style.format('{:.2f}').to_latex()

        reported_value = r'\bar ' + latex(self.symbol) + ' = ' + str(self.value) + r'\pm' + str(self.error)
        summary_items = (function_vars, expression, data, reported_value)
        summary_titles = ('Variables', 'Definición matemática', 'Datos tomados', 'Valor reportado')
        
        doc = Document('report')
        doc.preamble.append(Command('title', 'Summary of measurement of ' + '$' + latex(self.symbol) + '$'))
        doc.preamble.append(Command('author', 'Grupo 1'))
        doc.preamble.append(Command('date', NoEscape(r'\today')))
        doc.append(NoEscape(r'\maketitle'))
        for title, item in zip(summary_titles, summary_items):
            with doc.create(Section(title)):
                doc.append(Math(data=item, escape=False))
        
        if generate_pdf is True:
            doc.generate_pdf(clean_tex=True)
        if return_tex is True:
            return doc.dumps()  # The document as string in LaTeX syntax
        
    def constants(self, constant_observables=()):
        try:
            for observable in constant_observables:
                self.definition = self.definition.subs(observable.symbol, observable.value)
        except TypeError:
            print('Not valid observable type')
        