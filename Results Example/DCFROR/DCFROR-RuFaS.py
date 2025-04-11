#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 20:30:02 2023

@author: bradenlimb
"""
#%% Import Modules
from IPython import get_ipython
get_ipython().run_line_magic('reset', '-sf')
import pandas as pd
import numpy as np
import datetime
begin_time = datetime.datetime.now()

import sys
sys.path.append('../../../../../GitHub/DCFROR-Python')
from DCFROR import npv_calc, goal_seek, create_dcfror_input_dict, cashflow_plot, mpsp_plot, sankey_text, get_sankey_data, mpsp_plot_from_sankey, LCA_plot

import warnings
# Suppress only the specific warning message from openpyxl
warnings.filterwarnings("ignore", message = "Data Validation extension is not supported and will be removed")

#%% Evaluate the NPV

# Read inputs from Excel #TODO Change input file
excel_input_path = 'Model_Inputs-RuFaS Example.xlsx'

# excel_input_path = 'Model_Inputs-VT_direct.xlsx'

raw_inputs = pd.read_excel(excel_input_path, sheet_name=None, engine='openpyxl')
raw_fin = raw_inputs['Finance Assumptions']

dcfror_inputs = create_dcfror_input_dict(raw_inputs, raw_fin)

#%% Change inputs for sensitivity

# sensitivity_variables = {
#     'CAPEX': ['cost_capital_multiple'],
#     'Operation': ['cost_operational_items','cost_operational_units'],
#     'Production': ['unit_items','units_produced'],
        
#     }

# variable_type = 'CAPEX'
# variable_name = 'Total'
# change = 25/100
# change = -25/100
# # change = 0

# if len(sensitivity_variables[variable_type])>1:
#     if variable_name == 'Total':
#         dcfror_inputs[sensitivity_variables[variable_type][1]] *= (1+change)
#     else: 
#         array_index = dcfror_inputs[sensitivity_variables[variable_type][0]].index(variable_name)
#         dcfror_inputs[sensitivity_variables[variable_type][1]][array_index] *= (1+change)
# else:
#     if variable_name == 'Total':
#         dcfror_inputs[sensitivity_variables[variable_type][0]]['Cost'] *= (1+change)
#     else:  
#         dcfror_inputs[sensitivity_variables[variable_type][0]].loc[variable_name,'Cost'] *= (1+change)


#%% Run NPV Analysis
df_out = pd.DataFrame(index = [0], columns = ['Nickel Cost', 'Nickel LCA', 'Nickel Carbon Price','Cobalt Cost', 'Cobalt LCA', 'Cobalt Carbon Price'])

a_npv,a_cashflow = npv_calc(dcfror_inputs)

# Specify the input variable to optimize
change_variable = 'unit_cost'

# Set the initial bounds for the input variable
lower_bound = 1e-12 - 1
upper_bound = 1e4
bounds = [lower_bound,upper_bound]
# bounds = default_bounds(change_variable)

# Set the tolerance for the bisection method
tolerance = 1e-8

# Calculate the root using bisection
results_dict = goal_seek(npv_calc, 
                            dcfror_inputs, 
                            change_variable, 
                            bounds, 
                            tolerance)

# Save results values from optimization for outputing
optimized_input_value = results_dict['optimized_values']
optimized_pct_change = results_dict['optimized_pct_change']
base_value = results_dict['input_values']
final_dict = results_dict['updated_dcfror_dict']

dcfror_inputs[change_variable] = optimized_input_value
npv,cash_flow = npv_calc(dcfror_inputs)

print(f"Optimized value of {change_variable}:", optimized_input_value)
print("Percent Change from Base:", optimized_pct_change*100)

#%% Calculate the LCAs

raw_LCA = raw_inputs['LCA']
raw_LCA.set_index('Item', inplace=True)

# eGRID = raw_inputs['2021 eGrid Emissions']
# eGRID.set_index('Region', inplace=True)

# Ensure that operational items and LCA df use the same indexes
if not raw_LCA.index.equals(pd.Index(dcfror_inputs['cost_operational_items'])):
        raise ValueError("Indices of the two DataFrames are not the same.")
else:
    raw_LCA.reset_index(inplace=True)

# total_emissions = raw_LCA.loc['Total','Total Emissions (tonnes CO2e/yr)']
raw_LCA['total_emissions'] = raw_LCA['LCI'] * raw_LCA['Units Needed']
# total_emissions = 0
total_mass = raw_inputs['Revenue']['Units Produced'].sum() #Tonnes of Minerals
raw_LCA['LCA_per_mass'] = raw_LCA['total_emissions'] / total_mass # tonne CO2 per tonne Mineral
LCA = raw_LCA['LCA_per_mass'].sum()

#%% Calculate Carbon Price 

def carbon_price(traditional, carbon_mineralization):
    carbon_price = (carbon_mineralization['cost'] - traditional['cost']) / (traditional['ghg'] - carbon_mineralization['ghg'])
    return carbon_price

tradional_mining = raw_inputs['Traditional Mining']
tradional_mining.set_index('Mineral', inplace=True)

count = 0
for mineral in tradional_mining.index.tolist():
    traditional_vals = {
        'cost':  tradional_mining.loc[mineral, 'Cost ($/tonne Mineral)'],
        'ghg':   tradional_mining.loc[mineral, 'LCA (tonnes CO2/tonne Mineral)'] 
        }
    
    carbon_min_vals = {
        'cost':  optimized_input_value[count],
        'ghg':   LCA 
        }
    
    count += 1
    
    carbon_price_out = carbon_price(traditional_vals, carbon_min_vals)
    carbon_saved = tradional_mining.loc[mineral, 'LCA (tonnes CO2/tonne Mineral)'] - LCA
    
    df_out.loc[0, f'{mineral} Cost'] = carbon_min_vals['cost']
    df_out.loc[0, f'{mineral} LCA'] = carbon_min_vals['ghg']
    df_out.loc[0, f'{mineral} Carbon Price'] = carbon_price_out
    
    print(f'{mineral} carbon price is : ${carbon_price_out}')
    print(f"{mineral} carbon saved is : {carbon_saved}")
    
#%% Figures
save_fig_name = f'Cashflow'
cashflow_plot(cash_flow, save_fig = True, y_limits = [-40e3,30e3], y_interval = 1.0e4, save_fig_name = save_fig_name)

mineral_use = 'Crop'

# a = mpsp_plot(cash_flow, 
#               dcfror_inputs,
#               save_fig = True,
#               y_limits = None,
#               y_interval = None,
#               y_pcts = False,
#               products = [mineral_use],
#               save_fig_name = mineral_use)

sankey_str = sankey_text(cash_flow, 
                            dcfror_inputs,
                            y_pcts = False,
                            products = [mineral_use]
                            )

# Retrieve the DataFrame
sankey_df = get_sankey_data()

df_sankey_result = mpsp_plot_from_sankey(sankey_df, 
                                         save_fig=True, 
                                         y_limits=None, 
                                         y_interval=None, 
                                         y_pcts=False, 
                                         save_fig_name=f"{mineral_use} MSP",
                                         traditional_production=tradional_mining.loc[[mineral_use],'Cost ($/tonne Mineral)'].item(),
                                         subcategory_shades=True,
                                         combine_small_subcategories=True,
                                         product = mineral_use)

df_lca = LCA_plot(raw_LCA[['Item', 'LCA_per_mass']], 
                    save_fig=True, 
                    y_limits=None, 
                    y_interval=None, 
                    y_pcts=False, 
                    save_fig_name=f"{mineral_use} LCA",
                    traditional_production=tradional_mining.loc[[mineral_use],'LCA (tonnes CO2/tonne Mineral)'].item(),
                    product = mineral_use)

#%% End of Code
execute_time = datetime.datetime.now() - begin_time
print('')
print('Code execution time: ', execute_time)