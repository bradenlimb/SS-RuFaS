#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 12:42:04 2022

@author: bradenlimb
"""

#%% Import Modules
from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')

import pandas as pd
import sys
import datetime
import pickle
import os
import numpy as np
from tqdm import tqdm
begin_time = datetime.datetime.now()

# Must install nasspython module to run: https://pypi.org/project/nasspython/
import nasspython.nass_api as nass

#%% API Key

# Obtain API Key here: https://quickstats.nass.usda.gov/api
api_key = '156521EC-6EBD-3582-9294-E699DD64D910'

#%% Nass Data Function
def nass_data_out(api_key, 
                    source_desc_in,
                    sector_desc_in,
                    group_desc_in,
                    commodity_desc_in,
                    statisticcat_desc_in,
                    domain_desc_in,
                    short_desc_in,
                    agg_level_desc_in,
                    state_name_in,
                    year_in):
    
    if state_name_in is None:
        state_name_count = 1
    else:
        state_name_count = len(state_name_in)
        
    if year_in is None:
        year_count = 1
    else:
        year_count = len(year_in)
    
    total_runs = state_name_count*year_count
    print("Total Runs: ", total_runs)
    current_run = 0
    for i in range (state_name_count):
        state_name_use = state_name_in[i]
        
        for j in range(year_count):
            current_run += 1
            year_use = year_in[j]
            count = nass.nass_count(api_key, 
                                    source_desc = source_desc_in,
                                    sector_desc = sector_desc_in,
                                    group_desc = group_desc_in,
                                    commodity_desc = commodity_desc_in,
                                    statisticcat_desc = statisticcat_desc_in,
                                    domain_desc = domain_desc_in,
                                    short_desc = short_desc_in,
                                    agg_level_desc = agg_level_desc_in,
                                    state_name = state_name_use,
                                    year = year_use
                                    )
            print("Run ", current_run, " request count: ", count)
            if count > 50000:
                print("Request too large. Specify more parameters")
                sys.exit()
            else:
                output_data = nass.nass_data(api_key, 
                                        source_desc = source_desc_in,
                                        sector_desc = sector_desc_in,
                                        group_desc = group_desc_in,
                                        commodity_desc = commodity_desc_in,
                                        statisticcat_desc = statisticcat_desc_in,
                                        domain_desc = domain_desc_in,
                                        short_desc = short_desc_in,
                                        agg_level_desc = agg_level_desc_in,
                                        state_name = state_name_use,
                                        year = year_use
                                        )['data']
                
                df_data=pd.DataFrame(output_data) #Convert Dictionary to Pandas Dataframe
                remove_other_counties = True
                if remove_other_counties:
                    df_data.drop(df_data.index[df_data['county_code'] == '998'], inplace=True)
                df_data["fips"] = df_data["state_fips_code"]+df_data["county_code"]
                
                remove_columns = True
                if remove_columns:
                    keep_columns = ['fips',
                                    'country_name',
                                    'state_name',
                                    'county_name',
                                    'asd_desc',
                                    'freq_desc',
                                    'year',
                                    'short_desc',
                                    'Value',
                                    'unit_desc'
                                    ]
                    df_data = df_data.filter(keep_columns)
                df_data['Value'] = df_data['Value'].str.replace(',','')
                df_data['Value'] = pd.to_numeric(df_data['Value'], errors='coerce')
                
                if current_run == 1:
                    df_data_out = df_data
                elif current_run != 1:
                    df_data_out = pd.concat([df_data_out,df_data])
                    
    df_data_out = df_data_out.sort_values(by=['fips', 'year'])
    return df_data_out

def nass_find_commodities(api_key, 
                    source_desc_in,
                    sector_desc_in,
                    group_desc_in,
                    commodity_desc_in,
                    statisticcat_desc_in,
                    domain_desc_in,
                    short_desc_in,
                    agg_level_desc_in,
                    state_name_in,
                    year_in):
    
    if state_name_in is None:
        state_name_count = 1
    else:
        state_name_count = len(state_name_in)
        
    if year_in is None:
        year_count = 1
    else:
        year_count = len(year_in)
    
    total_runs = state_name_count*year_count
    print("Total Runs: ", total_runs)
    current_run = 0
    for i in range (state_name_count):
        state_name_use = state_name_in[i]
        
        for j in range(year_count):
            current_run += 1
            year_use = year_in[j]
            count = nass.nass_count(api_key, 
                                    source_desc = source_desc_in,
                                    sector_desc = sector_desc_in,
                                    group_desc = group_desc_in,
                                    commodity_desc = commodity_desc_in,
                                    statisticcat_desc = statisticcat_desc_in,
                                    domain_desc = domain_desc_in,
                                    short_desc = short_desc_in,
                                    agg_level_desc = agg_level_desc_in,
                                    state_name = state_name_use,
                                    year = year_use
                                    )
            print("Run ", current_run, " request count: ", count)
            if count > 50000:
                print("Request too large. Specify more parameters")
                sys.exit()
            else:
                output_data = nass.nass_data(api_key, 
                                        source_desc = source_desc_in,
                                        sector_desc = sector_desc_in,
                                        group_desc = group_desc_in,
                                        commodity_desc = commodity_desc_in,
                                        statisticcat_desc = statisticcat_desc_in,
                                        domain_desc = domain_desc_in,
                                        short_desc = short_desc_in,
                                        agg_level_desc = agg_level_desc_in,
                                        state_name = state_name_use,
                                        year = year_use
                                        )['data']
                
                
                
                df_data=pd.DataFrame(output_data) #Convert Dictionary to Pandas Dataframe
                df_data=pd.unique(df_data['commodity_desc'])

                if current_run == 1:
                    df_data_out = df_data
                elif current_run != 1:
                    df_data_out = df_data_out.append(df_data)
    return df_data_out
    
#%% Nass Data Inputs - Set placeholders to None
source_desc = None
sector_desc = None
group_desc = None
commodity_desc = None
statisticcat_desc = None
domain_desc = None
short_desc = None
agg_level_desc = None
state_name = [None]
year = [None]

#%% Nass Data Inputs
# Parameters can be found here: https://quickstats.nass.usda.gov/param_define
# Values can be found here: https://quickstats.nass.usda.gov/

# # CROP DATA
# sector_desc = 'CROPS'
# group_desc = 'FIELD CROPS'
# # group_desc = 'VEGETABLES'
# domain_desc = 'TOTAL'

# # commodity_desc = 'CORN'
# # commodity_desc = 'SOYBEANS'
# # commodity_desc = 'WHEAT'
# # commodity_desc = 'HAY & HAYLAGE'
# # commodity_desc = 'OATS'
# # commodity_desc = 'RYE'
# commodity_desc = 'BARLEY'

# statisticcat_desc = 'AREA HARVESTED'
# short_desc = f'{commodity_desc} - ACRES HARVESTED'

# # statisticcat_desc = 'PRODUCTION'
# # short_desc = f'{commodity_desc} - PRODUCTION, MEASURED IN BU'


# # short_desc = f'CORN, GRAIN - ACRES HARVESTED'
# # short_desc = 'CORN, GRAIN - PRODUCTION, MEASURED IN BU'
# # short_desc = 'CORN, GRAIN - YIELD, MEASURED IN BU / ACRE'

# # short_desc = 'HAY & HAYLAGE - PRODUCTION, MEASURED IN TONS, DRY BASIS'

# agg_level_desc = 'COUNTY'
# # state_name = ['IOWA','ILLINOIS','INDIANA'] # state_name input must be in a list
# # year = list(range(2017,2017 +1)) # year input must be in a list
# # year = list([2012]) # year input must be in a list
# # year = np.arange(2018, 2020+1, 1).tolist()

# source_desc = 'CENSUS'
# years = [2012,2017]#[1997,2002,2007,]

# Water Data
source_desc = 'CENSUS'
sector_desc = 'ECONOMICS'
group_desc = 'IRRIGATION'
commodity_desc = 'WATER'
statisticcat_desc = 'EXPENSE'
short_desc = f'WATER, IRRIGATION, SOURCE = OFF FARM - EXPENSE, MEASURED IN $ / ACRE FOOT'
domain_desc = 'TOTAL'
agg_level_desc = 'STATE' # NATION, STATE
years = [2023] #[2013, 2018, 2023]



# source_desc = 'SURVEY'
# years = np.arange(2018, 2020+1, 1).tolist()
#%% Pull Multiple Crop Data
run_loop = False
if run_loop:
    commodities = ['SWITCHGRASS','MISCANTHUS']#['OATS','RYE','COTTON','RICE','SORGHUM','BARLEY','CORN','SOYBEANS','WHEAT','OATS','RYE']#,,,['HAY & HAYLAGE']#
    categories = ['PRODUCTION','AREA HARVESTED']
    for commodity in tqdm(commodities):
        for category in categories:
            for year in years:
                commodity_desc = commodity
                statisticcat_desc = category
                year = list([year])
                
                if statisticcat_desc == 'AREA HARVESTED':
                    short_desc = f'{commodity_desc} - ACRES HARVESTED'
                    
                if statisticcat_desc == 'PRODUCTION':
                    short_desc = f'{commodity_desc} - PRODUCTION, MEASURED IN BU'
                    
                if commodity_desc =='CORN' or commodity_desc =='SORGHUM':
                    if statisticcat_desc == 'AREA HARVESTED':
                        short_desc = f'{commodity_desc}, GRAIN - ACRES HARVESTED'
                    if statisticcat_desc == 'PRODUCTION':
                        short_desc = f'{commodity_desc}, GRAIN - PRODUCTION, MEASURED IN BU'
                
                if commodity_desc =='HAY & HAYLAGE' and statisticcat_desc == 'PRODUCTION':
                    short_desc = 'HAY & HAYLAGE - PRODUCTION, MEASURED IN TONS, DRY BASIS'
                elif commodity_desc =='COTTON' and statisticcat_desc == 'PRODUCTION':
                    short_desc = 'COTTON - PRODUCTION, MEASURED IN BALES'
                elif commodity_desc =='RICE' and statisticcat_desc == 'PRODUCTION':
                    short_desc = 'RICE - PRODUCTION, MEASURED IN CWT'
                elif commodity_desc =='SWITCHGRASS' and statisticcat_desc == 'PRODUCTION':
                    short_desc = 'SWITCHGRASS - PRODUCTION, MEASURED IN TONS'
                elif commodity_desc =='MISCANTHUS' and statisticcat_desc == 'PRODUCTION':
                    short_desc = 'MISCANTHUS - PRODUCTION, MEASURED IN TONS'    
                    
                data_out = nass_data_out(api_key, 
                                    source_desc,
                                    sector_desc,
                                    group_desc,
                                    commodity_desc,
                                    statisticcat_desc,
                                    domain_desc,
                                    short_desc,
                                    agg_level_desc,
                                    state_name,
                                    year)
                
                
                
                save_to_excel = True
                if save_to_excel:
                    today = pd.to_datetime('today')
                    today_str = today.strftime('%Y-%m-%d~%H_%M_%S')
                    location = 'usda_data'
                    file_str = f'{today_str}_{agg_level_desc}_{commodity_desc}_{statisticcat_desc}'
                    file_str = f'{year[0]}_{source_desc}_{agg_level_desc}_{commodity_desc}_{statisticcat_desc}'
                    writer = pd.ExcelWriter(f'{location}/{file_str}.xlsx', engine='xlsxwriter')
                    data_out.to_excel(writer, sheet_name='Data', index=False)
                    writer.close() # Close the Pandas Excel writer and output the Excel file.



#%% Single Data Pull
simple_data = True
if simple_data:
    data_out = nass_data_out(api_key, 
                        source_desc,
                        sector_desc,
                        group_desc,
                        commodity_desc,
                        statisticcat_desc,
                        domain_desc,
                        short_desc,
                        agg_level_desc,
                        state_name,
                        years)

    # data_2 = nass_find_commodities(api_key, 
    #                     source_desc,
    #                     sector_desc,
    #                     group_desc,
    #                     commodity_desc,
    #                     statisticcat_desc,
    #                     short_desc,
    #                     agg_level_desc,
    #                     state_name,
    #                     year)
    # data_2 = data_2.tolist()
    
#%% Export Dataframe to Excel Spreadsheet
save_to_excel = True
if save_to_excel:
    # today = pd.to_datetime('today')
    # today_str = today.strftime('%Y-%m-%d~%H_%M_%S')
    # file_str = f'{today_str}_{agg_level_desc}_{commodity_desc}_{statisticcat_desc}'
    file_str = f'{years[0]}_{source_desc}_{agg_level_desc}_{commodity_desc}_{statisticcat_desc}'
    writer = pd.ExcelWriter(f'usda_data/{file_str}.xlsx', engine='xlsxwriter')
    data_out.to_excel(writer, sheet_name='Data', index=False)
    writer.close() # Close the Pandas Excel writer and output the Excel file.
    

    
#%% Export Dataframe to Pickel Spreadsheet
save_to_pickel = False
if save_to_pickel:
    root = os.getcwd()
    path = f"{root}/{group_desc}.pkl"
    with open(path, 'wb') as handle:
        pickle.dump(data_2, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    # path_veg = "/Users/bradenlimb/CloudStation/GitHub/CSU-ABM/specialty_codes/VEGETABLES.pkl"
    # VEGETABLES = pd.read_pickle(path_veg)
    
    # path_fc = "/Users/bradenlimb/CloudStation/GitHub/CSU-ABM/specialty_codes/FIELD CROPS.pkl"
    # FIELD_CROPS = pd.read_pickle(path_fc)

#%% End of Code
execute_time = datetime.datetime.now() - begin_time
print('Code execution time: ', execute_time)