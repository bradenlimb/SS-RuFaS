#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 21:23:38 2024

@author: bradenlimb
"""

#%% Import Modules
from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')
import pandas as pd
import numpy as np
import sys
from tqdm import tqdm
import itertools

import datetime
begin_time = datetime.datetime.now()

#%% Set Defaults

# year_use = 2021
PADDs = ['PADD 1A', 
         'PADD 1B', 
         'PADD 1C', 
         'PADD 2', 
         'PADD 3', 
         'PADD 4', 
         'PADD 5', 
         ]

#%% Loop Through Multiple Years
min_year = 2018
max_year = 2022

dict_years = {}

for year_use in range(min_year,max_year+1):

    #%% Load FIPS To Use
    
    # Set the file path to the desired file in the parent directory
    file_path = '../General Inputs/State Taxes.xlsx'
    
    # Read the Excel file, specifying the sheet, index column, and columns to keep
    sheet_name = 'State Taxes'  # Replace with your sheet name
    # index_col = 0  # Replace with the column index you want to use as the index
    # usecols = [0, 1, 2]  # Replace with the list of columns you want to keep
    
    # Load the data into a DataFrame
    df_fips = pd.read_excel(file_path, 
                            sheet_name=sheet_name, 
                            # index_col=index_col,
                            # dtype={"FIPS": str}
                                  )
    
    df_fips['fips'] = df_fips['FIPS']
    # Convert the column from number to string
    df_fips['fips'] = df_fips['fips'].astype(str)
    df_fips.loc[df_fips.fips.str.len()<5,"fips"]="0"+df_fips.fips
    # df_fips.set_index("fips",inplace=True)
    # df_fips[:] = np.nan
    
    for i in range(len(df_fips)):
        df_fips.loc[i,'state_fips'] = df_fips.loc[i,'fips'][0:2]
    
    # Correct values for the average values case
    df_fips.loc[df_fips['fips'] == '01','state_fips'] = "00"
    
    
    # asdf
    #%% Load the States + PADD Region and get the State FIP id
    # Load the States + PADD Region file
    file_path = '../General Inputs/PADD_Regions.xlsx'
    sheet_name = 'Use'  # Replace with your sheet name
    
    # Load the data into a DataFrame
    df_states = pd.read_excel(file_path, 
                            sheet_name=sheet_name
                                  )
    
    states_list = list(df_states['State'])
    df_states.set_index("State",inplace=True)
    
    
    # Load the States fips file
    file_path = '../General Inputs/State FIPS.xlsx'
    # sheet_name = 'Use'  # Replace with your sheet name
    
    # Load the data into a DataFrame
    df_state_fips = pd.read_excel(file_path,
                                  dtype={"Numeric code": str}
                                  )
    df_state_fips.loc[df_state_fips["Numeric code"].str.len()<2,"Numeric code"]="0"+df_state_fips["Numeric code"]
    df_state_fips.set_index("Name",inplace=True)
    
    # Combine state + PADD with State FIP id
    for state in states_list:
        if state == 'US': 
            df_states.loc[state,'state_fip'] = '00'
        else:
            df_states.loc[state,'state_fip'] = df_state_fips.loc[state,'Numeric code']
        
        
    #%% Add Electrcity Data to df_states
    
    
    # Load the Electricity data
    file_path = 'Electricity.xlsx'
    sheet_name = str(year_use)
    
    # Load the data into a DataFrame
    df_elec = pd.read_excel(file_path, 
                           sheet_name=sheet_name,
                          # dtype={"Date": str}
                          )
    df_elec.set_index("Name",inplace=True)
    
    # Combine Electricity data with df_states
    for state in states_list:
        conversion = 1/100 # converting from cents/kWh to $/kwh
        df_states.loc[state,'Grid_Electricity_Price_($/kwh)'] = df_elec.loc[state,'Average retail price (cents/kWh)'] * conversion
        
    #%% Add Natural Gas Data to df_states
    
    
    # Load the NG data
    file_path = 'Natural Gas - Commercial.xls'
    sheet_name = 'Use'
    
    # Load the data into a DataFrame
    df_ng = pd.read_excel(file_path, 
                          sheet_name=sheet_name,
                          # dtype={"Date": str}
                          )
    df_ng.set_index("Date",inplace=True)
    
    # Combine NG data with df_states
    for state in states_list:
        conversion = 1 # converting from thousand cubic feet to N/A
        df_states.loc[state,'Natural_Gas_Price_($/Mcf)'] = df_ng.loc[year_use,state] * conversion
        
    #%% Add Propane Data to df_states
    
    # Load the Propane data
    file_path = 'Propane - Wholesale.xls'
    sheet_name = 'Use'
    
    # Load the data into a DataFrame
    df_propane = pd.read_excel(file_path, 
                          sheet_name=sheet_name,
                          # dtype={"Date": str}
                          )
    df_propane.set_index("Date",inplace=True)
    
    # Combine propane data with df_states
    
    for state in states_list:
        conversion = 1  # gallon per gallon propane
        if state in df_propane.columns:
            df_states.loc[state,'Propane_Price_($/gal)'] = df_propane.loc[year_use,state] * conversion
            
        else:
            state_PADD = df_states.loc[state,'PADD']
            df_states.loc[state,'Propane_Price_($/gal)'] = df_propane.loc[year_use,state_PADD] * conversion
            
    #%% Add Gasoline Data to df_states
    
    # Load the Gasoline data
    file_path = 'Gasoline.xls'
    sheet_name = 'Use'
    
    # Load the data into a DataFrame
    df_gasoline = pd.read_excel(file_path, 
                          sheet_name=sheet_name,
                          # dtype={"Date": str}
                          )
    df_gasoline.set_index("Date",inplace=True)
    
    # Combine gasoline data with df_states
    
    for state in states_list:
        conversion = 1  #  gallon per gallon gasoline
        
        if state in df_gasoline.columns:
            df_states.loc[state,'Gasoline_Price_($/gal)'] = df_gasoline.loc[year_use,state] * conversion
            
        else:
            state_PADD = df_states.loc[state,'PADD']
            df_states.loc[state,'Gasoline_Price_($/gal)'] = df_gasoline.loc[year_use,state_PADD] * conversion
            
    #%% Add Diesel Data to df_states
    
    # Load the Gasoline data
    file_path = 'Diesel.xls'
    sheet_name = 'Use'
    
    # Load the data into a DataFrame
    df_diesel = pd.read_excel(file_path, 
                          sheet_name=sheet_name,
                          # dtype={"Date": str}
                          )
    df_diesel.set_index("Date",inplace=True)
    
    # Combine gasoline data with df_states
    
    for state in states_list:
        conversion = 1  #  gallon per gallon diesel
        
        if state in df_diesel.columns:
            df_states.loc[state,'Diesel_Price_($/gal)'] = df_diesel.loc[year_use,state] * conversion
            
        else:
            state_PADD = df_states.loc[state,'PADD']
            df_states.loc[state,'Diesel_Price_($/gal)'] = df_diesel.loc[year_use,state_PADD] * conversion
    
    #%% Add all fuel values to the fips data
    df_fips_out = df_fips[['fips','state_fips']]
    
    # get a list of unique state fips values
    state_fips_list = df_fips_out['state_fips'].unique().tolist()
    
    # set index value to the state fips so it's easier to reference
    df_states.set_index("state_fip",inplace=True)
    
    # create a list of output columns
    output_cols = ['Grid_Electricity_Price_($/kwh)','Natural_Gas_Price_($/Mcf)','Propane_Price_($/gal)','Gasoline_Price_($/gal)','Diesel_Price_($/gal)']
    
    for state_fip in state_fips_list:
        for output_col in output_cols:
            df_fips_out.loc[df_fips_out['state_fips'] == state_fip, output_col] = df_states.loc[state_fip, output_col]
            
    # Save the data to dictionary
    dict_years[str(year_use)] = df_fips_out
            
#%% Take the average of the specified annual dictionary values
# List the columns you want to average

# Select a template DataFrame to keep other columns (e.g., the first DataFrame)
template_df = dict_years[str(max_year)].copy()

# Calculate the mean across all DataFrames for the specified columns
average_df = pd.concat([df[output_cols] for df in dict_years.values()]).groupby(level=0).mean()

# Combine averaged columns with the non-averaged columns from the template DataFrame
template_df[output_cols] = average_df

# Add the averaged DataFrame as a new entry in the dictionary
dict_years[f'average_{min_year}-{max_year}'] = template_df


#%% Save data to excel file

# Define the output Excel file path
output_path = f'_geographic_data_{min_year}_{max_year}.xlsx'

# Write each DataFrame to a separate sheet
with pd.ExcelWriter(output_path) as writer:
    for sheet_name, df in dict_years.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
