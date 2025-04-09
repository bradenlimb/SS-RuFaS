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

from datetime import datetime
begin_time = datetime.now()

#%% Set Conversion Factors
# Conversion factor options for the conversions
conversion_factors = {
    'none': 1,
    'cwt_to_kg': 1/45.3592,
    'bushel-corn_to_kg': 1/25.401,
    'bushel-soy_to_kg': 1/27.2155,
    'ton-short_to_kg': 1/907.185,
    'ton-metric_to_kg': 1/1000,
    'gallon_to_liter': 1/3.78541,
    'cwt-milk_to_liters': 1/44.05,
    'mcf-natgas_to_mj': 1/28.3168 * 1/38, # First conversion to cubic meters from thousand cubic feet then to megajoules per cubic meters 
    'acre-foot_to_cubic-meters': 1/1233.48,
    'kgallon_to_cubic-meters': 1/3.78541,
    'acre_to_square-meters': 1/4046.86,
    }

#%% Set Commodity Options
commoditys_dict = {
    'cotton_seed': {
        'file_name': 'CottonCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'cotton_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'barley_seed': {
        'file_name': 'BarleyCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'barley_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'corn_seed': {
        'file_name': 'CornCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'corn_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'oat_seed': {
        'file_name': 'OatsCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'oat_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'peanut_seed': {
        'file_name': 'PeanutsCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'peanut_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'rice_seed': {
        'file_name': 'RiceCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'rice_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'sorghum_seed': {
        'file_name': 'SorghumCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'sorghum_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'soybean_seed': {
        'file_name': 'SoybeansCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'soybean_seed',
        'conversion_factor': 'acre_to_square-meters'
        },
    'wheat_seed': {
        'file_name': 'WheatCostReturn.xlsx',
        'in_units': 'dollar-per-acre',
        'out_units': 'dollar_per_square_meter',
        'save_name': 'wheat_seed',
        'conversion_factor': 'acre_to_square-meters'
        },

    
    }

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

#%% Load the USDA Regions by state
# Set the file path to the desired file in the parent directory
file_path = '../General Inputs/usda_ers_region_states.csv'
# Load the data into a DataFrame
df_usda = pd.read_csv(file_path)

#%% Import Crop Data

# Loop Through Commodities
for commodity_use in tqdm(commoditys_dict.keys()):
    
    #%% Load the commodity file
    # Load the data into a DataFrame
    df_commodity = pd.read_excel(commoditys_dict[commodity_use]['file_name'], 
                            sheet_name='Data sheet (machine readable)', 
                            # index_col=index_col,
                            # dtype={"FIPS": str}
                                  )
    df_commodity = df_commodity.loc[df_commodity['Item'] == 'Seed']
    
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
    
    # asdf
    # 
    #%% Create df_crop file
    regions_with_data = list(df_commodity['Region'].unique())
    regions_with_data.remove('U.S. total')
    
    states_with_data = df_usda[df_usda[regions_with_data].sum(axis=1) > 0]['State'].tolist()
    states_with_data.append('US')
    
    # Create df_crop dataframe
    df_crop = pd.DataFrame(columns = ['State','Value','Year'])
    
    def find_regions_by_state(state_name):
        # Find the row for that state
        state_row = df_usda[df_usda['State'] == state_name]
        
        # Get all region columns where the value is 1
        regions_for_state = state_row.loc[:, state_row.columns != 'State'].T
        regions = regions_for_state[regions_for_state[state_row.index[0]] == 1].index.tolist()
        
        return regions
    
    for state in states_with_data:
        if state == 'US':
            regions_by_state = ['U.S. total']
        else:
            regions_by_state = find_regions_by_state(state)
        
        df_state_data = df_commodity.loc[df_commodity['Region'].isin(regions_by_state)]
        
        state_years = list(df_state_data['Year'].unique())
        
        for year in state_years:
            i = len(df_crop)
            df_crop.loc[i,'State'] = state
            df_crop.loc[i,'Value'] = df_state_data.loc[df_state_data['Year'] == year, 'Value'].mean()
            df_crop.loc[i,'Year'] = year
    
    #%% Create a new df with year vs state
    unique_states = list(df_crop['State'].unique())
    unique_states.sort()
    
    years = list(df_crop['Year'].unique())
    years.sort()
    
    df_data = pd.DataFrame(index=years,columns=unique_states)
    
    for i in (range(len(df_crop))):
        state = df_crop.loc[i, 'State']
        year = df_crop.loc[i, 'Year']
        value = df_crop.loc[i, 'Value']
        if value != ' (NA)':
            df_data.loc[year,state] = value
        
    #%% Add Crop Data to df_states
    
    years_use = years
    
    # Combine crop data data with df_states
    for year in years_use:
        for state in unique_states:
            conversion = 1 
            if state != 'US':
                if state != 'District of Columbia':
                    state = state.title()
            df_states.loc[state, year] = df_data.loc[year,state] * conversion
        
    # Row index to use for filling NaN values
    row_index = 'US'
    
    # Fill NaN values in all columns using values from the specific row
    df_states = df_states.apply(lambda col: col.fillna(df_states.loc[row_index, col.name]))
    
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
    
    # Convert all columns from index 1 onwards to numeric while avoiding the warning
    for col in df_fips_out.columns[1:]:  # Skip the first column
        df_fips_out[col] = pd.to_numeric(df_fips_out[col], errors="coerce")
    
    #%% Conversions
    # Function to convert the df
    def convert_df(df, factor_name_in):
        factor = conversion_factors[factor_name_in]
    
        # Convert all values except first row and first column
        for row in range(0, df.shape[0]):
            for col in range(1, df.shape[1]):
                val = df.iat[row, col]
                if isinstance(val, str):
                    # Remove commas and convert to float
                    val_clean = val.replace(",", "").strip()
                    try:
                        df.iat[row, col] = float(val_clean) * factor
                    except ValueError:
                        df.iat[row, col] = val  # leave as is if not a number
                else:
                    df.iat[row, col] = float(val) * factor   
        
        return df
                    
    # Find conversion factor and convert the df
    factor_name = commoditys_dict[commodity_use]['conversion_factor']
    df_fips_out = convert_df(df_fips_out, factor_name)
    
    #%% Save Corn Grain as CSV
    save_name = commoditys_dict[commodity_use]['save_name']
    save_units = commoditys_dict[commodity_use]['out_units']
    
    filepath_out = f'../_RuFaS Input Files Correct Units/commodity_prices.{save_name}.{save_units}.csv'
    df_fips_out.to_csv(filepath_out, index=False, float_format="%.6g")  # 6 significant figures

