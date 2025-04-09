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
    }

#%% Set Commodity Options
commoditys_dict = {
    # 'class_II_milk': {
    #     'in_units': 'dollar-per-cwt',
    #     'out_units': 'dollar_per_liter',
    #     'save_name': 'milk_class_2',
    #     'conversion_factor': 'cwt-milk_to_liters'
    #     },
    # 'class_III_milk': {
    #     'in_units': 'dollar-per-cwt',
    #     'out_units': 'dollar_per_liter',
    #     'save_name': 'milk_class_3',
    #     'conversion_factor': 'cwt-milk_to_liters'
    #     },
    # 'class_IV_milk': {
    #     'in_units': 'dollar-per-cwt',
    #     'out_units': 'dollar_per_liter',
    #     'save_name': 'milk_class_4',
    #     'conversion_factor': 'cwt-milk_to_liters'
    #     },
    # 'nonfat_dry_milk': {
    #     'in_units': 'dollar-per-cwt',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'milk_nonfat_dry',
    #     'conversion_factor': 'cwt_to_kg'
    #     },
    # 'dry_whey': {
    #     'in_units': 'dollar-per-cwt',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'whey_dry',
    #     'conversion_factor': 'cwt_to_kg'
    #     },
    # 'cotton_seed_whole': {
    #     'in_units': 'dollar-per-short_ton',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'cotton_seed_whole',
    #     'conversion_factor': 'ton-short_to_kg'
    #     },
    # 'cotton_seed_meal': {
    #     'in_units': 'dollar-per-short_ton',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'cotton_seed_meal',
    #     'conversion_factor': 'ton-short_to_kg'
    #     },
    # 'cotton_seed_hulls': {
    #     'in_units': 'dollar-per-short_ton',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'cotton_seed_hulls',
    #     'conversion_factor': 'ton-short_to_kg'
    #     },
    # 'soybeans_hulls': {
    #     'in_units': 'dollar-per-short_ton',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'soybean_hulls',
    #     'conversion_factor': 'ton-short_to_kg'
    #     },
    # 'DDG_10_perc_moist': {
    #     'in_units': 'dollar-per-short_ton',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'distiller_grains_dried_10pct',
    #     'conversion_factor': 'ton-short_to_kg'
    #     },
    # 'MWDG_50_perc_moist': {
    #     'in_units': 'dollar-per-short_ton',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'distiller_grains_modified_wet_50pct',
    #     'conversion_factor': 'ton-short_to_kg'
    #     },
    # 'WDG_70_perc_moist': {
    #     'in_units': 'dollar-per-short_ton',
    #     'out_units': 'dollar_per_kilogram',
    #     'save_name': 'distiller_grains_wet_65pct',
    #     'conversion_factor': 'ton-short_to_kg'
    #     },
    'replacement_fresh_cow': {
        'in_units': 'dollar-per-head',
        'out_units': 'dollar_per_animal',
        'save_name': 'cow_dairy_fresh',
        'conversion_factor': 'none'
        },
    'replacement_T3_bred_cow': {
        'in_units': 'dollar-per-head',
        'out_units': 'dollar_per_animal',
        'save_name': 'cow_dairy_bred_t3',
        'conversion_factor': 'none'
        },
    'replacement_T3_bred_heifer': {
        'in_units': 'dollar-per-head',
        'out_units': 'dollar_per_animal',
        'save_name': 'cow_dairy_heifer_bred_t3',
        'conversion_factor': 'none'
        },
    'replacement_open_heifer': {
        'in_units': 'dollar-per-head',
        'out_units': 'dollar_per_animal',
        'save_name': 'cow_dairy_heifer_open',
        'conversion_factor': 'none'
        },
    'calves_bulls_no_1': {
        'in_units': 'dollar-per-cwt',
        'out_units': 'dollar_per_kilogram',
        'save_name': 'calf_bull_1',
        'conversion_factor': 'cwt_to_kg'
        },
    'calves_bulls_no_2': {
        'in_units': 'dollar-per-cwt',
        'out_units': 'dollar_per_kilogram',
        'save_name': 'calf_bull_2',
        'conversion_factor': 'cwt_to_kg'
        },
    'calves_heifers_no_1': {
        'in_units': 'dollar-per-cwt',
        'out_units': 'dollar_per_kilogram',
        'save_name': 'calf_heifer_1',
        'conversion_factor': 'cwt_to_kg'
        },
    'calves_heifers_no_2': {
        'in_units': 'dollar-per-cwt',
        'out_units': 'dollar_per_kilogram',
        'save_name': 'calf_ heifer_2',
        'conversion_factor': 'cwt_to_kg'
        },
    'feeder_holstein_300_500': {
        'in_units': 'dollar-per-cwt',
        'out_units': 'dollar_per_kilogram',
        'save_name': 'steer_holstein_300',
        'conversion_factor': 'cwt_to_kg'
        },
    'feeder_holstein_500_700': {
        'in_units': 'dollar-per-cwt',
        'out_units': 'dollar_per_kilogram',
        'save_name': 'steer_holstein_500',
        'conversion_factor': 'cwt_to_kg'
        },
    'feeder_holstein_700_1000': {
        'in_units': 'dollar-per-cwt',
        'out_units': 'dollar_per_kilogram',
        'save_name': 'steer_holstein_700',
        'conversion_factor': 'cwt_to_kg'
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

#%% Import Dairy Report Data

# Load the Excel file and target the specific sheet
file_path = "comp_dairy_report_raw_data_workbook.xlsx"
sheet_name = "comp_dairy_report_raw_data"

# Read the data from the specific sheet
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Convert it to a dictionary for quick lookup or access
units_dict = dict(zip(df["Commodity"], df["Units"]))

# Also store as a list of tuples if desired
units_list = list(zip(df["Commodity"], df["Units"]))

# Set the index to 'Commodity' for easier row selection
df.set_index('Commodity', inplace=True)

# Drop the 'Units' column
df = df.drop(columns='Units')

# Convert columns to datetime for grouping
df.columns = pd.to_datetime(df.columns)

# Resample the data annually and compute the average
annual_df = df.T.resample('Y').mean().T

# Rename columns to show year only
annual_df.columns = [col.year for col in annual_df.columns]

# Loop Through Commodities
for commodity_use in tqdm(commoditys_dict.keys()):

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
    
    
#%% Load Crop Data 
    ## TODO Select Type
    # commodity_use = "class_II_milk"
    
    # Create the DataFrame
    df_yearly_mean = pd.DataFrame(columns = ['Year','Value'])
    
    # Save the specified data to the yearly df
    def get_years_with_values(commodity):
        if commodity in annual_df.index:
            return annual_df.columns[~annual_df.loc[commodity].isna()].tolist()
        else:
            print(f"Commodity '{commodity}' not found in the dataset.")
            return []
    
    # Get values for the avalible years
    years_valid = get_years_with_values(commodity_use)
    
    for year in years_valid:
        i = len(df_yearly_mean)
        df_yearly_mean.loc[i,'Year'] = year
        df_yearly_mean.loc[i,'Value'] = annual_df.loc[commodity_use,year].astype(float)
    
    
    df_yearly_mean["Year"] = df_yearly_mean["Year"].astype(int)
    
    df_yearly_mean['State'] = 'US'
    
    df_crop = df_yearly_mean
    
    
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
            conversion = 1 # converting from dollars per bushel to N/A
            if state != 'US':
                state = state.title()
            df_states.loc[state, year] = df_data.loc[year,state.upper()] * conversion
        
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

