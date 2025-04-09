#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 15:12:17 2025

@author: bradenlimb
"""

import pandas as pd
from datetime import datetime

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

