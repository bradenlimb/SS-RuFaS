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

import warnings
# Suppress only the specific warning message from openpyxl
warnings.filterwarnings("ignore", message = "Data Validation extension is not supported and will be removed")


#%% NPV Calculation Function

def npv_calc(input_dict):
    
    """
    This function calculates the Net Present Value (NPV) using a dicounted cash flow rate of return analysis.
    
    Parameters:
        input_dict (dictionary): Dictonary that includes economic inputs

    Returns:
        npv (float): Net Present Value of the analysis
        cash_flow (Pandas DataFrame): Table with a year by year breakdown of system economics.
        
    """
    
    # cost_cap = input_dict['cost_capital']
    cost_cap_multi = input_dict['cost_capital_multiple']
    cost_cap_total = cost_cap_multi['Cost'].sum()
    cost_op = (input_dict['cost_operational_units'] * input_dict['cost_operational_unit_cost']).sum(axis=0) # This can be an array or single value
    cost_rev = (input_dict['units_produced'] * input_dict['unit_cost']).sum(axis=0) # This can be arrays or single values
    
    # Assumptions and data extraction from raw_fin
    loan_int = input_dict['loan_interest_rate']
    loan_term = input_dict['loan_term']
    loan_amt = input_dict['loan_amount']
    equity_amt = input_dict['equity_amount']

    con_int = input_dict['construction_interest_rate']
    con_term = input_dict['construction_term']
    con_finish = input_dict['construction_finish_pcts']

    tax_rate = input_dict['tax_rate']
    irr = input_dict['internal_rate_of_return']
    
    project_term = input_dict['project_term']
    
    dep_rate = input_dict['depreciation_rate']
    dep_rate = dep_rate[~np.isnan(dep_rate)]
    dep_term = len(dep_rate)

    # Initialize Cash Flow Table
    columns = ["Year", "Capital", "LoanPayment", "InterestPayment", "LoanPrinciple", "Revenue", "OperationCosts",
               "DepreciationRate", "CapitalDepreciation", "NetRevenue", "LossesForward", "TaxableIncome", "IncomeTax","TaxCreditUsed","TaxCreditRevenue",
               "CashIncome", "DiscountFactor", "PresentValue", "NPVCapitalPlusInterest", "NPVTax","NPVTaxCreditUsed","NPVTaxCreditRevenue", "NPVRevenue", "NPVRevenuePlotting",
               "NPVOperationCosts", "NPVCapitalCosts"]
    
    cash_flow = pd.DataFrame(index=range(-con_term + 1, project_term + 1), columns=columns)

    # Fill in the year column
    cash_flow['Year'] = cash_flow.index
    cash_flow.fillna(0, inplace=True)

    # Calculate Discount Rates
    cash_flow['DiscountFactor'] = 1 / (1 + irr) ** cash_flow['Year']
    
        # Add multiple capital costs and different loans to the cash flow
    for index in cost_cap_multi.index.tolist():
        cost_cap = cost_cap_multi.loc[index,'Cost']
        construction_yr = cost_cap_multi.loc[index,'Construction Year']
        loan_term = cost_cap_multi.loc[index,'Loan Term']
        
        cash_flow_temp = cash_flow.copy(deep=True)
        cash_flow_temp[cash_flow_temp.columns] = 0

        # Calculations for Construction Years
        for i in range(-con_term + 1, 1):
            I = i + construction_yr
            cash_flow_temp.at[I, 'Capital'] += cost_cap * equity_amt * con_finish[i + con_term - 1]
        
            
            if I == -con_term + 1 + construction_yr:
                cash_flow_temp.at[I, 'LoanPrinciple'] = cost_cap * con_finish[i + con_term - 1] * loan_amt
            else:
                cash_flow_temp.at[I, 'LoanPrinciple'] = cost_cap * con_finish[i + con_term - 1] * loan_amt + cash_flow_temp.at[I - 1, 'LoanPrinciple']
            cash_flow_temp.at[I, 'InterestPayment'] = cash_flow_temp.at[I, 'LoanPrinciple'] * con_int
    
            cash_flow_temp.at[I, 'NPVCapitalPlusInterest'] = (cash_flow_temp.at[I, 'Capital'] + cash_flow_temp.at[I, 'InterestPayment']) * cash_flow.at[I, 'DiscountFactor']
            cash_flow_temp.at[I, 'NPVCapitalCosts'] = cash_flow.at[I, 'DiscountFactor'] * cash_flow_temp.at[I, 'Capital']
        
        # Calculations for Operating Years
        loan_pmt = (cost_cap * loan_int * loan_amt) / (1 - (1 + loan_int) ** (-loan_term))
        cash_flow_temp.loc[1+construction_yr:loan_term+construction_yr, 'LoanPayment'] = loan_pmt
        
        # a[index] = cash_flow_temp.copy()
        cash_flow += cash_flow_temp

    cash_flow.loc[1:project_term, 'Revenue'] += cost_rev
    cash_flow.loc[1:project_term, 'OperationCosts'] = cost_op

    cash_flow.loc[1:dep_term, 'DepreciationRate'] = dep_rate[:min(dep_term, project_term)]
    cash_flow.loc[1:dep_term, 'CapitalDepreciation'] = cost_cap_total * dep_rate[:min(dep_term, project_term)]

    for i in range(1, project_term + 1):
        
        cash_flow.at[i, 'InterestPayment'] = cash_flow.at[i - 1, 'LoanPrinciple'] * loan_int
        cash_flow.at[i, 'LoanPrinciple'] = cash_flow.at[i - 1, 'LoanPrinciple'] - cash_flow.at[i, 'LoanPayment'] + cash_flow.at[i, 'InterestPayment']

        cash_flow.at[i, 'NetRevenue'] = cash_flow.at[i, 'Revenue'] - cash_flow.at[i, 'InterestPayment'] - cash_flow.at[i, 'OperationCosts'] - cash_flow.at[i, 'CapitalDepreciation']

        if cash_flow.at[i, 'NetRevenue'] <= 0:
            cash_flow.at[i, 'LossesForward'] = cash_flow.at[i, 'NetRevenue'] + cash_flow.at[i - 1, 'LossesForward']
            cash_flow.at[i, 'TaxableIncome'] = 0
        else:
            carry_forward_limit = 0.8 #https://www.investopedia.com/terms/t/tax-loss-carryforward.asp#:~:text=Key%20Takeaways%3A&text=Net%20operating%20losses%20(NOLs)%2C,year%20the%20carryforward%20is%20used.
            if cash_flow.at[i, 'NetRevenue'] <= abs(cash_flow.at[i - 1, 'LossesForward']) * carry_forward_limit :
                cash_flow.at[i, 'LossesForward'] = cash_flow.at[i, 'NetRevenue'] + cash_flow.at[i - 1, 'LossesForward']
                cash_flow.at[i, 'TaxableIncome'] = 0
            else:
                cash_flow.at[i, 'TaxableIncome'] = cash_flow.at[i, 'NetRevenue'] + cash_flow.at[i - 1, 'LossesForward'] * carry_forward_limit
                cash_flow.at[i, 'LossesForward'] = cash_flow.at[i - 1, 'LossesForward'] * (1 - carry_forward_limit)
            
        if (cash_flow.at[i, 'TaxableIncome'] > 0):
            tax_amt = cash_flow.at[i, 'TaxableIncome'] * tax_rate
            cash_flow.at[i, 'IncomeTax'] = tax_amt
        else:
            cash_flow.at[i, 'IncomeTax'] = 0

        cash_flow.at[i, 'CashIncome'] = cash_flow.at[i, 'Revenue'] + cash_flow.at[i, 'TaxCreditRevenue'] - cash_flow.at[i, 'LoanPayment'] - cash_flow.at[i, 'OperationCosts'] - cash_flow.at[i, 'IncomeTax']
        cash_flow.at[i, 'PresentValue'] = cash_flow.at[i, 'CashIncome'] * cash_flow.at[i, 'DiscountFactor']

        cash_flow.at[i, 'NPVLoanPayment'] = cash_flow.at[i, 'DiscountFactor'] * cash_flow.at[i, 'LoanPayment']
        cash_flow.at[i, 'NPVTax'] = cash_flow.at[i, 'DiscountFactor'] * cash_flow.at[i, 'IncomeTax']
        cash_flow.at[i, 'NPVTaxCreditUsed'] = cash_flow.at[i, 'DiscountFactor'] * cash_flow.at[i, 'TaxCreditUsed']
        cash_flow.at[i, 'NPVTaxCreditRevenue'] = cash_flow.at[i, 'DiscountFactor'] * cash_flow.at[i, 'TaxCreditRevenue']
        cash_flow.at[i, 'NPVRevenue'] = cash_flow.at[i, 'DiscountFactor'] * cash_flow.at[i, 'Revenue']
        cash_flow.at[i, 'NPVOperationCosts'] = cash_flow.at[i, 'DiscountFactor'] * cash_flow.at[i, 'OperationCosts']

    cash_flow['NPVRevenuePlotting'] = cash_flow['NPVRevenue'] #- cash_flow['NPVTaxCreditRevenue']
    npv = cash_flow['PresentValue'].sum() - cash_flow['NPVCapitalPlusInterest'].sum()
    return npv, cash_flow

#%% Create input dictionary for DCFROR

def create_dcfror_input_dict(raw_inputs, raw_fin):
    
    # Fix formating for contruction finish percentages
    if isinstance(raw_fin.loc[raw_fin['Variable_Name'] == 'con_finish', 'Value'].values[0], int):
        item = raw_fin.loc[raw_fin['Variable_Name'] == 'con_finish', 'Value'].values[0]
        construction_finish_pcts = [float(item) / 100]
    else:
        construction_finish_pcts = [float(item) / 100 for item in raw_fin.loc[raw_fin['Variable_Name'] == 'con_finish', 'Value'].values[0].replace(" ","").split(",")]
    
    dcfror_inputs = {
        # 'cost_capital': raw_inputs['Capital Costs'].iloc[0,1],
        'cost_capital_multiple': raw_inputs['Capital Costs'],
        'cost_operational_items': list(raw_inputs['Operation Costs']['Item']),
        'cost_operational_units': raw_inputs['Operation Costs']['Units Needed'],
        'cost_operational_unit_cost': raw_inputs['Operation Costs']['Unit Cost'],
        'units_produced': np.array(raw_inputs['Revenue']['Units Produced']),
        'unit_cost': np.array(raw_inputs['Revenue']['Unit Cost']),
        'unit_optimize': np.array(raw_inputs['Revenue']['Optimize']),
        'unit_items': list(raw_inputs['Revenue']['Item']),
        
        # Assumptions and data extraction from raw_fin
        'loan_interest_rate': raw_fin.loc[raw_fin['Variable_Name'] == 'int_loan', 'Value'].values[0],
        'loan_term': int(raw_fin.loc[raw_fin['Variable_Name'] == 'loan_term', 'Value'].values[0]),
        'loan_amount': raw_fin.loc[raw_fin['Variable_Name'] == 'loan_amt', 'Value'].values[0],
        'equity_amount': raw_fin.loc[raw_fin['Variable_Name'] == 'equity_amt', 'Value'].values[0],
        'construction_finish_pcts': construction_finish_pcts,
        'construction_interest_rate': raw_fin.loc[raw_fin['Variable_Name'] == 'int_con', 'Value'].values[0],
        'construction_term': int(raw_fin.loc[raw_fin['Variable_Name'] == 'con_term', 'Value'].values[0]),
    
        'tax_rate': raw_fin.loc[raw_fin['Variable_Name'] == 'tax_rate', 'Value'].values[0],
        'internal_rate_of_return': raw_fin.loc[raw_fin['Variable_Name'] == 'irr', 'Value'].values[0],
        
        'project_term': int(raw_fin.loc[raw_fin['Variable_Name'] == 'project_term', 'Value'].values[0]),
        
        # Depreciation Values
        'depreciation_rate': np.array(raw_inputs['MACRS'][raw_fin.loc[raw_fin['Variable_Name'] == 'depreciation_term', 'Value'].values[0]]) / 100
        
        }
    
    dcfror_inputs['cost_capital_multiple'].set_index('Item',inplace=True)
    # dcfror_inputs['cost_capital'] = dcfror_inputs['cost_capital_multiple']['Cost'].sum()
    
    return dcfror_inputs


#%% Goal Seek Function
def goal_seek(function, 
              input_dict, 
              change_variable, 
              bounds = [1e-12 - 1, 1e4], # This chooses the default method for the percent increase method
              tolerance = 1e-8 # Tolerance for the bisection method - decrease the tolerance size to get NPV closer to zero
              ):
    
    eject = False
    
    if change_variable == 'units_produced' or change_variable == 'unit_cost':
        multiplier_array = input_dict['unit_optimize']
        ones_array = np.ones_like(input_dict[change_variable])

        # Check if input_dict[change_variable] is a 2D array and adjust multiplier_array
        if input_dict[change_variable].ndim == 2:
            # Repeat multiplier_array along the second dimension
            multiplier_array = np.tile(multiplier_array[:, np.newaxis], (1, input_dict[change_variable].shape[1]))

    else:
        multiplier_array = 1
        ones_array = 1
    
    base_value = input_dict[change_variable]
    low_bound = multiplier_array*bounds[0]
    high_bound = multiplier_array*bounds[1]
    
    count = 0
    bound_difference = bounds[1]-bounds[0]
    while bound_difference > tolerance:
        count += 1
        
        input_dict[change_variable] = base_value * (ones_array+low_bound)
        f_low = function(input_dict)[0]
        # print(input_dict[change_variable],f_low)
        
        input_dict[change_variable] = base_value * (ones_array+high_bound)
        f_high = function(input_dict)[0]
        # print(input_dict[change_variable],f_high)
        
        midpoint = (low_bound + high_bound) / 2
        input_dict[change_variable] = base_value * (ones_array+midpoint)
        f_mid = function(input_dict)[0]
        
        
        # Check if both values are of the same sign
        if f_high * f_low > 0:
            # Check if both values are positive
            if f_high > 0 and f_low > 0:
                warnings.warn(f"DCFROR Goal Seek Error: NPV will always be positive for a feasible value of {change_variable} - adjust inputs accordingly.")
                eject = True
            # Check if both values are negative
            elif f_high < 0 and f_low < 0:
                warnings.warn(f"DCFROR Goal Seek Error: NPV will always be negative for a feasible value of {change_variable} - adjust inputs accordingly.")
                eject = True
                
            if eject:
                output_dict = {
                    'optimized_values': base_value * (np.nan),
                    'input_values': base_value,
                    'optimized_pct_change': np.atleast_1d(np.nan),
                    'updated_dcfror_dict': input_dict
                    }
                return output_dict
                
                
        elif f_mid == 0:
            print(count)
            return midpoint
        elif f_mid * f_low < 0:
            high_bound = multiplier_array*midpoint
        else:
            low_bound = multiplier_array*midpoint
            
        if isinstance(low_bound, np.ndarray):
            bound_difference = abs(low_bound - high_bound).sum()
        else:
            bound_difference = abs(low_bound - high_bound)
        
    # print(count)
    midpoint = (low_bound + high_bound) / 2
    input_dict[change_variable] = base_value * (ones_array+midpoint)
    
    output_dict = {
        'optimized_values': base_value * (ones_array+midpoint),
        'input_values': base_value,
        'optimized_pct_change': np.atleast_1d(midpoint),
        'updated_dcfror_dict': input_dict
        }
    
    return output_dict


#%% Create the input dictionary from the excel inputs file

if __name__ == "__main__":

    # Read inputs from Excel 
    excel_input_path = 'Appendix B - RuFaS DFROR Example w Cashflow.xlsx'
    
    raw_inputs = pd.read_excel(excel_input_path, sheet_name=None, engine='openpyxl')
    raw_fin = raw_inputs['Finance Assumptions']
    
    dcfror_inputs = create_dcfror_input_dict(raw_inputs, raw_fin)
    
    #%% Run NPV Analysis
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
