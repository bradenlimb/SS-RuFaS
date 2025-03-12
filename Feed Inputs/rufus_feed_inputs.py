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
import json

import datetime
begin_time = datetime.datetime.now()

#%% Set Defaults


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
#%% Load the Feed Defualt JSON File
# JSON file paths
rufas_github_path = '/Users/bradenlimb/CloudStation/GitHub/RuFAS/input/data/feed/'
file_path_json = rufas_github_path + 'default_feed.json'

# Open the JSON file and load data
with open(file_path_json, "r") as file:
    json_feed_defaults = json.load(file)

#%% Keep only keys that end with "_feeds"
json_feed_defaults_feeds = {key: value for key, value in json_feed_defaults.items() if key.endswith("_feeds") and key != "purchased_feeds" and key != "farm_grown_feeds"}
json_feed_defaults_feeds['all'] = set(num for values in json_feed_defaults_feeds.values() for num in values)

#%% Load the CSV file
# Create file path to csv
file_path_csv = rufas_github_path + 'NASEM_Comp_with_TDN.csv'

# Load the data into a DataFrame
df_feed_defaults = pd.read_csv(file_path_csv)

#%% Create dictionary with dfs for each default feed list
dict_feed_defaults = {}

for key in json_feed_defaults_feeds.keys():
    ids_use = json_feed_defaults_feeds[key]
    dict_feed_defaults[key] = df_feed_defaults[df_feed_defaults["rufas_id"].isin(ids_use)]
    
#%% Save dictionary to Excel file
excel_filename = "default_feeds.xlsx"
with pd.ExcelWriter(excel_filename, engine="xlsxwriter") as writer:
    for sheet_name, df in dict_feed_defaults.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)  # Save each df to a sheet

print(f"Excel file '{excel_filename}' has been saved successfully.")