#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 12 14:09:58 2025

@author: bradenlimb
"""

#%% Import Modules
from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')
import pandas as pd
import numpy as np
import sys
import os
from tqdm import tqdm


import datetime
begin_time = datetime.datetime.now()

#%% Set Defaults
item = "Almond Hulls"
years = ['2022','2023','2024']


#%% Combine all data for each year

# Create dictionary for annual data
annual_data = []

# Loop through the years
for year in years:
    
    folder_path = f'{item}/{year}'
    
    # Get all CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
    
    # Initialize an empty list to store DataFrames
    data_list = []
    
    # Loop through each file and process it
    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        
        # Filter DataFrame for the specified commodity
        df = df.loc[df['commodity'] == item]
        df.reset_index(drop=True, inplace=True)
        
        if not df.empty:  # Ensure the DataFrame is not empty
            data_list.append({
                'date': df.loc[0, 'report end date'],
                'price': df['avg price'].mean()
            })
    
    # Combine all dictionary elements into a single DataFrame
    combined_df = pd.DataFrame(data_list)
    
    # Remove duplicates based only on the 'date' column
    combined_df.drop_duplicates(subset=['date'], inplace=True)
    
    # Save the annual data
    annual_data.append({
        'Year': year,
        'Value': df['avg price'].mean() 
            })
    
# Combine all dictionary elements into a single DataFrame
annual_data_df = pd.DataFrame(annual_data)
    
#%% Save the combined DataFrame to a CSV file
output_path = f"{item}_annual_prices_dollar-per-ton.csv"
annual_data_df.to_csv(output_path, index=False)
# https://mymarketnews.ams.usda.gov/public_data