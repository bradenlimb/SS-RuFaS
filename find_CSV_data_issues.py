#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 12 10:54:53 2025

@author: bradenlimb
"""

#%% Import modules
import os
import glob
import pandas as pd
from tqdm import tqdm

#%% Setup
# Specify the directory containing CSV files
directory = '_RuFaS Input Files/'

# List to collect invalid entries
invalid_entries = []

# Loop through all CSV files in the directory
for filepath in glob.glob(os.path.join(directory, '*.csv')):
    df = pd.read_csv(filepath, index_col=0)
    df.index.name = 'fips'
    
    needs_fix = False
    # 1) Detect & replace bad markers in each column
    for col in df.columns:
        # identify '(D)' or '(NA)'
        mask_bad = df[col].astype(str).str.strip().isin(['(D)', '(NA)'])
        if mask_bad.any():
            needs_fix = True
            valid = df.loc[~mask_bad, col]
            first_val = valid.iloc[0] if not valid.empty else pd.NA
            df.loc[mask_bad, col] = first_val
    
    # 2) Optionally save
    original_name = os.path.basename(filepath)
    if needs_fix:
        base, _ = os.path.splitext(filepath)
        fixed_path = f"{base}_fix.csv"
        df.to_csv(fixed_path)
        report_name = os.path.basename(fixed_path)
    else:
        report_name = original_name
    
    # 3) Numeric validation on the (possibly cleaned) df
    for fips, row in df.iterrows():
        for year, value in row.items():
            if pd.isna(value) or (isinstance(value, str) and value.strip() == ''):
                continue
            try:
                float(value)
            except (ValueError, TypeError):
                invalid_entries.append({
                    'file': report_name,
                    'fips': fips,
                    'year': year,
                    'value': value
                })


# Report results
if invalid_entries:
    result_df = pd.DataFrame(invalid_entries)
    print("Invalid entries found:")
    print(result_df.to_string(index=False))
else:
    print("All values in all CSV files are numeric. Cleaned files saved with '_fix.csv'.")