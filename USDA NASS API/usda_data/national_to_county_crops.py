#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 16:46:15 2022

@author: bradenlimb
"""

#%% Import Modules
from IPython import get_ipython
get_ipython().magic('reset -sf')
import pandas as pd
from sklearn.preprocessing import normalize
import numpy as np
import os
import shutil
import glob

#%% Import Data
categories = ['PRODUCTION','AREA HARVESTED','OPERATIONS']
# statisticcat_desc = categories[0]
year = 2017

biocrop_list = ['MISCANTHUS','SWITCHGRASS']
commodity_desc = biocrop_list[0]

file_location = '/Users/bradenlimb/CloudStation/GitHub/CSU-ABM/input_data/usda_data'
file_name = f'{year}_CENSUS_COUNTY_{commodity_desc}_PRODUCTION_use.xlsx'
# file_name_split = os.path.splitext(file_name)
# file_name_out = file_name_split[0] + '_new' + file_name_split[1]
sheet_names = ['Data','County-Raw','State','National']

data_dict = {}

for sheet_name in sheet_names:
    
    df_temp = pd.DataFrame()
    
    
    if sheet_name != 'Data':
        df_temp = pd.read_excel (rf'{file_location}/{file_name}',
                                  sheet_name = sheet_name )
        for statisticcat_desc in categories:
            if commodity_desc in biocrop_list and statisticcat_desc == 'PRODUCTION':
                short_desc = f'{commodity_desc} - PRODUCTION, MEASURED IN TONS' 
            elif commodity_desc in biocrop_list and statisticcat_desc == 'AREA HARVESTED':
                short_desc = f'{commodity_desc} - ACRES HARVESTED' 
            elif commodity_desc in biocrop_list and statisticcat_desc == 'OPERATIONS':
                short_desc = f'{commodity_desc} - OPERATIONS WITH AREA HARVESTED'
            
            df_temp_2 = df_temp.loc[(df_temp['Data Item'] == short_desc) & (df_temp['Domain'] == 'TOTAL') & (df_temp['Year'] == year)].copy(deep=True) 
            df_temp_2['Value'] = pd.to_numeric(df_temp_2['Value'], errors='coerce')  
            data_dict[f'{sheet_name}_{statisticcat_desc}'] = df_temp_2
    else:
        df_temp = pd.read_excel (rf'{file_location}/{file_name}',
                                  sheet_name = sheet_name,
                                  dtype={"fips": str})
        data_dict[f'{sheet_name}'] = df_temp
    
Z = data_dict['County-Raw_OPERATIONS']
z = data_dict['State_PRODUCTION']

#%% Setup Data for Calculations

df_county_data = data_dict['Data'].copy(deep=True) 
df_data = df_county_data[['fips','country_name','state_name','county_name']]

states = df_data.state_name.unique().tolist()
states.append('ALL')
countries = df_data.country_name.unique().tolist()*len(states)
counties = data_dict['County-Raw_OPERATIONS'].County.unique().tolist()

df_other = pd.DataFrame({'country_name':countries,'state_name':states,'county_name':['ALL']*len(states),'fips':np.NaN*len(states)})
df_other.sort_values(by=['state_name'],inplace=True)

df_data = pd.concat([df_other,df_data], axis=0)
# df_data.sort_values(by=['county_name', 'state_name'],inplace=True)
df_data.reset_index(inplace=True,drop=True)
        
for statisticcat_desc in categories:
    df_temp_3 = pd.DataFrame()
    sheet_name = 'National'
    df_temp_3 = data_dict[f'{sheet_name}_{statisticcat_desc}']
    df_data.loc[(df_data['country_name'] == 'UNITED STATES') & (df_data['state_name'] == 'ALL') & (df_data['county_name'] == 'ALL'),statisticcat_desc] = df_temp_3.Value.item()
    
for statisticcat_desc in categories:
    df_temp_4 = pd.DataFrame()
    sheet_name = 'State'
    df_temp_4 = data_dict[f'{sheet_name}_{statisticcat_desc}']
    for state in states:
        if state == 'ALL':
            continue
        df_data.loc[(df_data['state_name'] == state) & (df_data['county_name'] == 'ALL'),statisticcat_desc] = df_temp_4.loc[df_temp_4['State'] == state].Value.item()
        
for statisticcat_desc in categories:
    df_temp_5 = pd.DataFrame()
    sheet_name = 'County-Raw'
    df_temp_5 = data_dict[f'{sheet_name}_{statisticcat_desc}']
    for county in counties:
        df_data.loc[(df_data['county_name'] == county),statisticcat_desc] = df_temp_5.loc[df_temp_5['County'] == county].Value.item()
        
#%% Import Prisim Data

yeild_path = '/Users/bradenlimb/CloudStation/BETO-ABM-MOEA/GIS Data/Primary Biofuel Potential Production Sheet_v1.xlsx'

df_prisim = pd.read_excel (yeild_path,
                          sheet_name = commodity_desc.capitalize(),
                          dtype={"GEOID": str},
                          usecols=["GEOID","Average Areal Yield (mg/ha)"]) 
df_prisim.rename(columns={"GEOID":"fips", "Average Areal Yield (mg/ha)":'yeild (mg/ha)'},inplace=True)
df_prisim.loc[df_prisim.fips.str.len()<5,"fips"]="0"+df_prisim.fips
# df_prisim.set_index('fips',inplace=True)
df_prisim.sort_values(by='fips',inplace=True)
df_prisim.reset_index(drop=True,inplace=True)

for fip in df_data.loc[df_data.fips.notnull()].fips.tolist():
    df_data.loc[df_data['fips'] == fip,'prism yeild mg/acre'] = df_prisim.loc[df_prisim['fips'] == fip]['yeild (mg/ha)'].item()
    
for state in states:
    if state == 'ALL':
        continue
    df_data.loc[(df_data['prism yeild mg/acre'].isnull())&(df_data['state_name'] == state)&(df_data['county_name'] == 'ALL'),'prism yeild mg/acre'] = df_data.loc[(df_data['prism yeild mg/acre'].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] != 'ALL'),'prism yeild mg/acre'].mean()
    
#%% Estimate Values on State Level

state = 'ALL'
county = 'ALL'
categories = ['PRODUCTION','AREA HARVESTED']
statisticcat_desc = 'PRODUCTION'

weighted_average = True
for statisticcat_desc in categories:
    if not weighted_average or statisticcat_desc == 'AREA HARVESTED':
    
    
        val_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == 'ALL')&(df_data['county_name'] == 'ALL'),statisticcat_desc].item()
        val_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),statisticcat_desc].sum()
        val_remaining = val_total-val_used
        
        ops_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == 'ALL')&(df_data['county_name'] == 'ALL'),'OPERATIONS'].item()
        ops_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),'OPERATIONS'].sum()
        ops_remaining = ops_total-ops_used
        
        df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['county_name'] == 'ALL'),statisticcat_desc] = val_remaining*df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['county_name'] == 'ALL'),'OPERATIONS']/ops_remaining
    
    # for 
    
        for state in states:
            if state == 'ALL':
                continue
            
            val_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] == 'ALL'),statisticcat_desc].item()
            val_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] != 'ALL'),statisticcat_desc].sum()
            val_remaining = val_total-val_used
            
            ops_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] == 'ALL'),'OPERATIONS'].item()
            ops_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] != 'ALL'),'OPERATIONS'].sum()
            ops_remaining = ops_total-ops_used
            
            df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] == state),statisticcat_desc] = val_remaining*df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] == state),'OPERATIONS']/ops_remaining
    
        df_data['calc yeild ton/acre'] = df_data['PRODUCTION']/df_data['AREA HARVESTED']


    else:
    
        val_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == 'ALL')&(df_data['county_name'] == 'ALL'),statisticcat_desc].item()
        val_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),statisticcat_desc].sum()
        val_remaining = val_total-val_used
        
        ops_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == 'ALL')&(df_data['county_name'] == 'ALL'),'OPERATIONS'].item()
        ops_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),'OPERATIONS'].sum()
        ops_remaining = ops_total-ops_used
        
        yeild_weighted_sum = sum(df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),'OPERATIONS']*df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),'prism yeild mg/acre'])
        temp_list = df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),'OPERATIONS']*df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] != 'ALL')&(df_data['county_name'] == 'ALL'),'prism yeild mg/acre']
        df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['county_name'] == 'ALL'),statisticcat_desc] = val_remaining*temp_list/yeild_weighted_sum
    
        for state in states:
            if state == 'ALL':
                continue
            
            val_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] == 'ALL'),statisticcat_desc].item()
            val_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] != 'ALL'),statisticcat_desc].sum()
            val_remaining = val_total-val_used
            
            ops_total = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] == 'ALL'),'OPERATIONS'].item()
            ops_used = df_data.loc[(df_data[statisticcat_desc].notnull())&(df_data['state_name'] == state)&(df_data['county_name'] != 'ALL'),'OPERATIONS'].sum()
            ops_remaining = ops_total-ops_used
            
            yeild_weighted_sum = sum(df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] == state),'OPERATIONS']*df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] == state),'prism yeild mg/acre'])
            temp_list = df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] == state),'OPERATIONS']*df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] == state),'prism yeild mg/acre']
            df_data.loc[(df_data[statisticcat_desc].isnull())&(df_data['state_name'] == state),statisticcat_desc] = val_remaining*temp_list/yeild_weighted_sum
                
        df_data['calc yeild ton/acre'] = df_data['PRODUCTION']/df_data['AREA HARVESTED']

#%% Backup Raw Files and Save New Files

categories = ['PRODUCTION','AREA HARVESTED']

file_location = '/Users/bradenlimb/CloudStation/GitHub/CSU-ABM/input_data/usda_data'
file_name_a = f'2017_CENSUS_COUNTY_{commodity_desc}'

save_excel = False

if save_excel:
    for category in categories:
        original = rf'{file_location}/{file_name_a}_{category}.xlsx'
        target = rf'{file_location}/{file_name_a}_{category}_raw.xlsx'
        
        if os.path.exists(target):
            target_split = os.path.splitext(target)
            numoffiles = len(glob.glob(rf'{target_split[0]}*'))
            target = target_split[0] + f'_{numoffiles}' + target_split[1]
        
        shutil.copyfile(original, target)
        
        df_out = pd.read_excel (original,
                                  sheet_name = 'Data',
                                  dtype={"fips": str})
        fips = []
        fips = df_out.fips.tolist()
        for fip in fips:
            df_out.loc[df_out['fips'] == fip,'Value'] = df_data.loc[df_data['fips'] == fip,category].item()
        
        # Save New Files
        df_out.to_excel(original,
                 sheet_name='Data',
                 index=False)  


