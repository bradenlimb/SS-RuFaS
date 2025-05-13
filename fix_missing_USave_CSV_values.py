#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 13 11:11:26 2025

@author: bradenlimb
"""

import os
import glob
import pandas as pd

def compute_us_avg(df_counties: pd.DataFrame) -> pd.Series:
    """
    Given df_counties indexed by county‐FIPS (strings),
    detect state‐level vs. true county data and compute national average.
    Returns a Series named '1'.
    """
    df = df_counties.copy()
    df.index = df.index.astype(str)
    state_codes = df.index.str[:-3]
    grouped = df.groupby(state_codes)

    # detect state-level: any state with >1 row must have identical values
    is_state_level = (
        any(g.shape[0] > 1 for _, g in grouped) and
        all((g.nunique() <= 1).all() for _, g in grouped if g.shape[0] > 1)
    )

    if is_state_level:
        state_df = grouped.first()
        us = state_df.mean(axis=0, skipna=True)
    else:
        us = df.mean(axis=0, skipna=True)

    us.name = '1'
    return us

def fill_missing_us_avg(directory: str, pattern: str = "*.csv"):
    for path in glob.glob(os.path.join(directory, pattern)):
        # 1) read all columns as strings so index_col stays string
        df = pd.read_csv(path, index_col=0, dtype=str)
        # 2) ensure index is string
        df.index = df.index.astype(str)
        # 3) convert any numeric columns
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')

        # if no US row at all → prepend complete US average
        if '1' not in df.index:
            df_counties = df
            us_avg = compute_us_avg(df_counties)
            df_out = pd.concat([us_avg.to_frame().T, df])
            df_out.to_csv(path)
            print(f"Inserted full U.S. average into {os.path.basename(path)}")
            continue

        # find which columns are missing in the existing US row
        missing_cols = df.loc['1'][df.loc['1'].isna()].index.tolist()
        if not missing_cols:
            print(f"✓ {os.path.basename(path)}: no missing U.S. values.")
            continue

        # recompute averages and fill only the missing ones
        df_counties = df.drop('1', errors='ignore')
        us_avg = compute_us_avg(df_counties)
        df.loc['1', missing_cols] = us_avg[missing_cols]

        # overwrite
        df.to_csv(path)
        print(f"→ Filled {len(missing_cols)} missing values in {os.path.basename(path)}: {missing_cols}")
        
if __name__ == "__main__":
    # point this at your folder of CSVs
    input_dir = "_RuFaS Input Files/"
    # input_dir = "untitled folder/"
    fill_missing_us_avg(input_dir)