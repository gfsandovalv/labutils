from os import stat
from statistics import covariance
from tkinter import Y
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import t

class LinModel():
    def __init__(self, slope_name='m', intercept_name='b', dataframe=None, takes=()) -> None:
        
        self.slope_name = slope_name
        self.intercept_name = intercept_name
          
    def single_take_run(self, 
            dataframe=None,
            xlabel='x', ylabel='y', xseries=None, yseries=None):
        
        self.xlabel = xlabel
        self.ylabel = ylabel
        
        if xseries is not None:
            x = xseries.copy()
            y = yseries.copy()
        else:  
            x = dataframe[xlabel].copy()
            y = dataframe[ylabel].copy()
        
        def stat_error(std, dof):
            t_95 = t.isf(0.025, dof)
            return std*t_95

        coefficients, covariance_matrix = np.polyfit(x, y, 1, cov=True)
        fit = np.poly1d(coefficients)
        
        yhat = fit(x)                         # or [p(z) for z in x]
        ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
        ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
        sstot = np.sum((y - ybar)**2)
        r_value = ssreg / sstot   

        m, b = coefficients
        std_m, std_b = np.sqrt(np.diag(covariance_matrix))
        unc_m, unc_b = (stat_error(std_m, len(x)-2), stat_error(std_b, len(x)-2))

        stat_summary = pd.DataFrame(
            data={
                'Parámetro' : [self.slope_name, self.intercept_name, 'R^2'], 
                'Valor estimado':[m, b, r_value],
                'Error estándar': [std_m, std_b, None], 
                'Incertidumbre':[unc_m, unc_b, None]
            }, index=['slope', 'intercept', 'r_value'])
        
        m = stat_summary['Valor estimado'].loc['slope']
        b = stat_summary['Valor estimado'].loc['intercept']
        f = lambda x: m*x + b
        
        return stat_summary, f
    
    def run_for_takes(self, takes=(), xlabel='x', ylabel='y'):
        self.takes = takes
        summaries = {}
        fit_functions = {}
        for i, take in enumerate(self.takes):
            summaries[i], fit_functions[i] = self.single_take_run(dataframe=take, xlabel=xlabel, ylabel=ylabel)

        self.summaries = summaries
        self.fit_functions = fit_functions

        takes_summaries = pd.concat(tuple(summaries.values()))
        total_summary = pd.DataFrame(data={'Parámetro': [self.slope_name, self.intercept_name]}, columns=['Parámetro', 'Valor estimado', 'Incertidumbre'], index=['slope', 'intercept'])

        N = len(summaries)

        instrumental_error = 0.03
        for index in total_summary.index:
            total_summary.loc[index]['Valor estimado'] = takes_summaries.loc[index]['Valor estimado'].mean()
            total_summary.loc[index]['Incertidumbre'] = (takes_summaries.loc[index]['Incertidumbre'].pow(2).sum() + instrumental_error**2)**0.5/N
        
        m = total_summary['Valor estimado'].loc['slope']
        b = total_summary['Valor estimado'].loc['intercept']
        self.mean_fit = lambda x: m*x + b
        self.total_summary = total_summary
        return total_summary
        
    
    def plot_single_take(
        self, 
        take=None, ## dataframe of take data
        yerr=None, xerr=None, ## error for error bar plot
        x_var_name='x', y_var_name='y', ## name for axis and legend
        data_label='data', ## name for data points in legend
        colors=['orange', 'red'], ## fit and data points colors
        plot_data=True,  plot_fit=True, 
        x_var_units = 'x_units', y_var_units = 'y_units', ## units for x and y
        significant_figures=1, ## significant figures for rounding parameters
        show_function_dependency=True, ## if true the y axis label is formmated as y(x)
        adimensional_x_y=(False, False), # show units for x and y axis
        fitted_func=lambda x: x,
        ls='--', show_expression=True
        ):
        if plot_data is True:
            x = take[self.xlabel]
            y = take[self.ylabel]
        
        m = fitted_func(1) - fitted_func(0)
        b = fitted_func(0)
                
        self.ln_expression_latex = '$' + y_var_name + '(' + x_var_name + ') = ' + str(round(m, significant_figures)) + x_var_name + ' + ' + str(round(b, significant_figures)) + '$' if show_expression is True else ''
                    
        #self.stat_info_latex = '\n$R^2 = $' + str(round(self.ln_result.rvalue**2, 4)) + '\n $\sigma_{N-1} = $' + str(round(self.ln_result.stderr, 5))
        if plot_data == True:
            plt.errorbar(x, y, 
                         yerr=yerr, xerr=xerr, 
                         marker = '.', ls='none', ms='5',
                         color = colors[0], ecolor = colors[1], 
                         elinewidth = 2, capsize=5, 
                         label=data_label)
        if plot_fit == True:
            x = self.takes[0][self.xlabel]
            plt.plot(x, x.apply(fitted_func), 
                     ls=ls, color=colors[1], label=self.ln_expression_latex)
                        
            
        ylabel = '$' + y_var_name + '(' + x_var_name + ')' + '$' if show_function_dependency else '$' + y_var_name + '$'
            
        xlabel = '$' + x_var_name + '$'
            
        if adimensional_x_y[0] is False:
            xlabel = xlabel + ' (' + x_var_units + ')'
        if adimensional_x_y[1] is False:
            ylabel = ylabel + ' (' + y_var_units + ')'
            
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)   
        plt.legend()
        
    def plot_for_takes(
        self, 
        yerr=None, xerr=None, ## error for error bar plot
        x_var_name='x', y_var_name='y', ## name for axis and legend
        data_labels=['data'], ## name for data points in legend
        colors_array=[['orange', 'orange'], ['red', 'red']], ## fit and data points colors
        plot_data=True,  plot_fit=True, 
        x_var_units = 'x_units', y_var_units = 'y_units', ## units for x and y
        significant_figures=1, ## significant figures for rounding parameters
        show_function_dependency=True, ## if true the y axis label is formmated as y(x)
        adimensional_x_y=(False, False), # show units for x and y axis
        ):
        
        for i, take in enumerate(self.takes):
            self.plot_single_take(
                take=take, yerr=yerr, xerr=xerr, 
                data_label=data_labels[i], colors=colors_array[i], plot_data=plot_data, plot_fit=plot_fit, significant_figures=significant_figures, show_function_dependency=show_function_dependency, adimensional_x_y=adimensional_x_y, fitted_func=self.fit_functions[i], show_expression=False)
        self.plot_single_take(plot_data=False, fitted_func=self.mean_fit, ls='-.', colors=['', 'green'], x_var_name=x_var_name, y_var_name=y_var_name, 
        x_var_units=x_var_units, y_var_units=y_var_units, 
        plot_fit=plot_fit, significant_figures=significant_figures, show_function_dependency=show_function_dependency, adimensional_x_y=adimensional_x_y, yerr=yerr, xerr=xerr)
        #plt.plot(self.takes[0]['cos_theta_sq'], self.mean_fit(self.takes[0]['cos_theta_sq']), ls='-.', label='Promedio')
        #plt.legend()
        