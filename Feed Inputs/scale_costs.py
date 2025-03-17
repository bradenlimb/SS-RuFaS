#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 12:06:26 2025

@author: bradenlimb
"""

#%% Import Modules
from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')
import pandas as pd

#%% User Inputs

# Years to keep
year_low = 2020
year_high = 2023
years = list(map(str, range(year_low, year_high + 1)))

# Scaling Factor
# scale = 85/74 # Value for Alfalfa Silage from USDA "Costs of Forage Production" USDA vs Corn Silage
scale = 104/109 # Value for Barley Silage from beefresearch.ca vs Corn Silage - https://www.beefresearch.ca/blog/silage-cost-of-production/


# Input File
file_in  = '../_RuFaS Input Files/crops_corn-silage-price-recieved_dollar-per-ton.csv'

#%% Load the input file
df_in = pd.read_csv(file_in)

# Set 'Year' column as the index
df_in.set_index('fips', inplace=True)

#%% Keep only certain years
df_in = df_in[years]

#%% Scale the df
df_out = df_in * scale

#%% Save as CSV
# filepath_out = '../_RuFaS Input Files/feeds_alfalfa-silage_dollar-per-ton.csv'
filepath_out = '../_RuFaS Input Files/feeds_barley-silage_dollar-per-ton.csv'
df_out.to_csv(filepath_out, index=True, float_format="%.6g")  # 6 significant figures
