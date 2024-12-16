#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 16:24:04 2024

@author: bradenlimb
"""

#%% Import Modules
import pandas as pd
from geopy.geocoders import Nominatim
import requests
from tqdm import tqdm

#%% Load Data
# Load the Excel spreadsheet with city and state data
df = pd.read_excel('PNNL_water_rates_with_fips.xlsx')  # Update with your file path


# #%% ##TODO - Calculate correct escalation rate

# # Function to calculate escalation rate
# def calc_escalation_rate(cost_1, year_1, cost_2, year_2):
#     escalation_rate = (cost_2/cost_1)**(1/(year_2-year_1))-1
#     return escalation_rate

# for i in df.index.tolist():
#     df.loc[i, 'Actual Escalation Rate'] = calc_escalation_rate(df.loc[i, 'First Year Rate ($ per kGal)'], 
#                                                                df.loc[i, 'First Year'], 
#                                                                df.loc[i, 'Final Year Rate ($ per kGal)'], 
#                                                                df.loc[i, 'Final Year'], 
#                                                                )

# #%% Find County and FIPS
# # Geolocator for city-to-county lookup
# geolocator = Nominatim(user_agent="county_fips_lookup")

# # Function to get county and FIPS code using TIGERweb API
# def get_county_fips(city, state_abbr):
#     try:
#         # Geocode to find the county
#         location = geolocator.geocode(f"{city}, {state_abbr}")
#         if location:
#             lat, lon = location.latitude, location.longitude
#             # Use TIGERweb API to find the FIPS code based on coordinates
#             response = requests.get(
#                 f"https://geo.fcc.gov/api/census/area?lat={lat}&lon={lon}&format=json"
#             )
#             data = response.json()
#             if 'results' in data and data['results']:
#                 county_name = data['results'][0]['county_name']
#                 fips = data['results'][0]['county_fips']
#                 return county_name, fips
#     except Exception as e:
#         print(f"Error processing {city}, {state_abbr}: {e}")
#     return None, None

# # Apply the function to each row
# tqdm.pandas()  # Enable tqdm with pandas
# df[['County', 'FIPS']] = df.progress_apply(lambda row: pd.Series(get_county_fips(row['City'], row['State'])), axis=1)

# # Add State FIPS to this
# df['State FIPS'] = [fip[:2] for fip in df['FIPS']]

# # Save the results back to Excel
# df.to_excel('PNNL_water_rates_with_fips.xlsx', index=False)
 

#%% Find yearly data

# Find bounds
min_year = df['First Year'].min()
# max_year = df['Final Year'].max()
max_year = 2023
years = list(range(min_year, max_year + 1))

# Find column names
# Sort by FIPS
df.sort_values(by='FIPS', ascending = True, inplace = True)
df.reset_index(inplace = True, drop = True)

fip_prev = None
count = 0
for i in df.index.tolist():
    fip = df.loc[i,"FIPS"]
    if fip == fip_prev:
        if count == 0:
            count = 1
            df.loc[i-1,'col_name'] = f'{fip_prev}_1'
        count += 1
        df.loc[i,'col_name'] = f'{fip}_{count}'
    else:
        count = 0
        df.loc[i,'col_name'] = f'{fip}'
    
    fip_prev = fip

# Setup df for yearly data
df_yearly = pd.DataFrame(index = years, columns = list(df['col_name']))

# Loop through each entry to get the yearly data
for i in df.index.tolist():
    start_year = df.loc[i,'First Year']
    # end_year = df.loc[i,'Final Year']
    end_year = max_year
    escalation_rate = df.loc[i, 'Actual Escalation Rate']
    col_name = df.loc[i, 'col_name']
    
    # Set first year rate
    df_yearly.loc[start_year,col_name] = df.loc[i,'First Year Rate ($ per kGal)']
    
    # Loop through the remaining years
    for year in list(range(start_year + 1, end_year + 1)):
        df_yearly.loc[year,col_name] = df_yearly.loc[year - 1,col_name] * (1+escalation_rate)
        
    if start_year > min_year:
        for year in list(range(start_year - 1, min_year - 1, -1)):
            deescalation_rate = 1 / (1+escalation_rate)
            df_yearly.loc[year,col_name] = df_yearly.loc[year + 1,col_name] * deescalation_rate



#%% Load the States + Water Region and get the State FIP id
##TODO - Add data for the state level and/or water region level
# Load the States + Water Region file
file_path = 'Water_Regions.xlsx'
sheet_name = 'Use'  # Replace with your sheet name

# Load the data into a DataFrame
df_states = pd.read_excel(file_path, 
                        sheet_name=sheet_name
                              )

states_list = list(df_states['State'])
df_states.set_index("State",inplace=True)


# Load the States fips file
file_path = '../../General Inputs/State FIPS.xlsx'
# sheet_name = 'Use'  # Replace with your sheet name

# Load the data into a DataFrame
df_state_fips = pd.read_excel(file_path,
                              dtype={"Numeric code": str}
                              )
df_state_fips.loc[df_state_fips["Numeric code"].str.len()<2,"Numeric code"]="0"+df_state_fips["Numeric code"]
df_state_fips.set_index("Name",inplace=True)

# Combine state + Water Region with State FIP id
for state in states_list:
    if state == 'US': 
        df_states.loc[state,'state_fip'] = '00'
    else:
        df_states.loc[state,'state_fip'] = df_state_fips.loc[state,'Numeric code']
        
        
#%% Load FIPS To Use

# Set the file path to the desired file in the parent directory
file_path = '../../General Inputs/State Taxes.xlsx'

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

#%% Create df for all water values
fips_use = list(df_fips['fips'])
df_water = pd.DataFrame(index = fips_use, columns = years)

# Loop through the values to find the correct data to use
for fip in fips_use:
    
    # Identify the columns to average
    # Check if county data exists first
    if len(df.loc[df['FIPS'] == fip]) > 0:
        
        # Get columns for that fip
        col_names = list(df.loc[df['FIPS'] == fip,'col_name'])
        
        # Loop through the years to find the average value for the state
        for year in years:
            df_water.loc[fip,year] = df_yearly.loc[year,col_names].mean()
        
    # Check if state data exists next
    elif len(df.loc[df['State FIPS'] == fip[0:2]]) > 0:
        
        # Get columns for that state
        col_names = list(df.loc[df['State FIPS'] == fip[0:2],'col_name'])
        
        # Loop through the years to find the average value for the state
        for year in years:
            df_water.loc[fip,year] = df_yearly.loc[year,col_names].mean()
    
    # If US average then average all state values
    elif fip == '01':
        # Loop through the years to find the average value for the state
        for year in years:
            df_water.loc[fip,year] = df_yearly.loc[year,:].mean()
    
    # Last resort is water region data
    else:
        
        # Get columns for that water region
        water_region_use = df_states.loc[df_states['state_fip'] == fip[0:2], 'Water Region'].item()
        
        # Get locations in that water region
        col_names = list(df.loc[df['Water Region'] == water_region_use,'col_name'])
        
        # Loop through the years to find the average value for the state
        for year in years:
            df_water.loc[fip,year] = df_yearly.loc[year,col_names].mean()
    
# Save the results back to Excel
df_water.to_csv('../../_RuFaS Input Files/water_retail_dollar-per-kgal.csv', index=True)
