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
# min_year = 2018
# max_year = 2022

# dict_years = {}

# for year_use in range(min_year,max_year+1):

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
    
    
#%% Load Propane Data 

## TODO Select Propane Type
data_type = 'Retail' # Wholesale, Retail

# Set the inputs
file_path = f'Propane - {data_type}.xls'
sheet_name = 'Use'

# Load the data into a DataFrame
df_propane = pd.read_excel(file_path, 
                      sheet_name=sheet_name,
                      # dtype={"Date": str}
                      )
df_propane.set_index("Date",inplace=True)

# asdf

#%% Add Propane Data to df_states

years_use = df_propane.index.tolist()

# Combine Propane data data with df_states
for year in years_use:
    for state in states_list:
        conversion = 1  # gallon per gallon propane
        if state in df_propane.columns:
            df_states.loc[state, year] = round(df_propane.loc[year,state] * conversion,6)
            
        else:
            state_PADD = df_states.loc[state,'PADD']
            df_states.loc[state, year] = round(df_propane.loc[year,state_PADD] * conversion,6)
            
# asdf
#%% Reformat to the  fips data
df_fips_out = df_fips[['fips','state_fips']]

# get a list of unique state fips values
state_fips_list = df_fips_out['state_fips'].unique().tolist()

# set index value to the state fips so it's easier to reference
df_states.set_index("state_fip",inplace=True)

# create a list of output columns
output_cols = years_use

for state_fip in state_fips_list:
    for output_col in output_cols:
        df_fips_out.loc[df_fips_out['state_fips'] == state_fip, output_col] = df_states.loc[state_fip, output_col]
        
df_fips_out.drop(columns=['state_fips'], inplace = True)

#%% Save as CSV
filepath_out = f'../_RuFaS Input Files/propane_{data_type.lower()}_dollar-per-gallon.csv'
df_fips_out.to_csv(filepath_out, index = False)
