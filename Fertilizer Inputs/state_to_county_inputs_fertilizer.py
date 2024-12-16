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
    
    
#%% Load Fertilizer Data 

# Set the inputs
file_path = 'Aggregated Data.xlsx'
sheet_name = 'Use'

# Load the data into a DataFrame
df_fert = pd.read_excel(file_path, 
                      sheet_name=sheet_name,
                      # dtype={"Date": str}
                      )
df_fert.set_index("Year",inplace=True)

# asdf

#%% Add Fertilizer Data to all fips

# Find the years
years_use = df_fert.index.tolist()

# Find the fertilizer types
fertilizer_types = df_fert.columns.tolist()

# Produce csv for each fertilizer type
for fertilizer in fertilizer_types:
    
    # Setup fips df
    df_fips_out = df_fips[['fips']]
    
    # Iterate through the years
    for year in years_use:
    
        conversion = 1  # short ton
        df_fips_out.loc[:,year] = round(df_fert.loc[year,fertilizer] * conversion,2)

    # Save as CSV
    fertilizer_name = fertilizer.replace(" ", "-").lower()
    filepath_out = f'../_RuFaS Input Files/fertilizer_{fertilizer_name}_dollar-per-shortton.csv'
    df_fips_out.to_csv(filepath_out, index = False)
