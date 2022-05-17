import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t

class LinModel():
    def __init__(self) -> None:
        pass
    
    def run(self, dataframe=None, 
                 xlabel='x', ylabel='y', xseries=None, yseries=None, 
                 slope_name='m', intercept_name='b'):
        
        if xseries is not None:
            self.x = xseries
            self.y = yseries
        else:  
            self.x = dataframe[xlabel].copy()
            self.y = dataframe[ylabel].copy()
        
        def stat_error(std, dof):
            t_95 = t.isf(0.025, dof)
            return std*t_95

        coef, cov = np.polyfit(self.x, self.y, 1, cov=True)

        self.m, self.b = coef
        std_m, std_b = np.sqrt(np.diag(cov))
        unc_m, unc_b = (stat_error(std_m, len(self.x)-2), stat_error(std_b, len(self.x)-2))

        self.stat_summary = pd.DataFrame(
            data={
                'Parámetro' : [slope_name, intercept_name], 
                'Valor estimado':[self.m, self.b],
                'Error estándar': [std_m, std_b], 
                'Incertidumbre':[unc_m, unc_b]
            }, index=['slope', 'intercept'])
        
    def prediction_func(self, x):
        return self.m*x + self.b   
    
    def plot(self, yerr=None, xerr=None, 
             x_var_name='x', y_var_name='y', 
             colors=['orange', 'red'], 
             plot_data=True, data_label='data', plot_fit=True, 
             x_var_units = 'xunits', y_var_units = 'yunits', significant_figures=1,
             show_function_dependency=True, adimensional_x_y=(False, False)):
        
        self.ln_expression_latex = '$' + y_var_name + '(' + x_var_name + ') = ' + str(round(self.m, significant_figures)) + x_var_name + ' + ' + str(round(self.b, significant_figures)) + '$'
                
        #self.stat_info_latex = '\n$R^2 = $' + str(round(self.ln_result.rvalue**2, 4)) + '\n $\sigma_{N-1} = $' + str(round(self.ln_result.stderr, 5))
        if plot_data == True:
            plt.errorbar(self.x, self.y, yerr=yerr, xerr=xerr, marker = '.', ls='none', ms='5',color = colors[0], ecolor = colors[1], elinewidth = 2, capsize=5, label=data_label)
        if plot_fit == True:
            plt.plot(self.x, self.x.apply(self.prediction_func), ls='--', color=colors[1], label=self.ln_expression_latex)
            
        
        ylabel = '$' + y_var_name + '(' + x_var_name + ')' + '$' if show_function_dependency else '$' + y_var_name + '$'
        
        xlabel = '$' + x_var_name + '$'
        
        if adimensional_x_y[0] is False:
            xlabel = xlabel + ' (' + x_var_units + ')'
        if adimensional_x_y[1] is False:
            ylabel = ylabel + ' (' + y_var_units + ')'
        
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
                
        plt.legend() 