#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 13 11:23:10 2025

@author: bradenlimb
"""

"""
compile_us_averages.py

Iterates through all CSV files in a directory, extracts the U.S. average (first row) for each year,
and compiles them into a single CSV table with:
  - Rows: CSV filenames
  - Columns: Every year from the global minimum to maximum year found across files
  - Cells: The U.S. average value from each file for that year (NaN if not present)

Usage:
    python compile_us_averages.py
"""
import os
import glob
import pandas as pd

def compile_us_averages(input_dir: str, output_path: str):
    # Store per-file US averages
    us_data = {}
    min_year = None
    max_year = None

    # Pattern to find all CSVs
    pattern = os.path.join(input_dir, "*.csv")
    for filepath in glob.glob(pattern):
        filename = os.path.basename(filepath)
        # Read with first column as index (county-FIPS) and all data as strings
        df = pd.read_csv(filepath, index_col=0, dtype=str)

        # Convert column names to int (years) and values to numeric
        print(filename)
        df.columns = [int(col) for col in df.columns]
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Extract the first row (U.S. average)
        us_series = df.iloc[0]

        # Update global year range
        file_min = int(us_series.index.min())
        file_max = int(us_series.index.max())
        min_year = file_min if min_year is None else min(min_year, file_min)
        max_year = file_max if max_year is None else max(max_year, file_max)

        filename_no_csv = filename[:-4]
        filename_no_csv = filename_no_csv.replace(".", "_")
        us_data[filename_no_csv] = us_series

    # Build combined DataFrame with complete year span
    years = list(range(min_year, max_year + 1))
    combined_df = pd.DataFrame(index=us_data.keys(), columns=years)

    # Populate with values (NaN for missing years)
    for fname, series in us_data.items():
        combined_df.loc[fname, series.index] = series.values
        
    # 1) Change the *index name* (the label of the index, not its values)
    combined_df.index.name = "commodity"  # give the index a descriptive name
    
    # 2) Sort all rows by that index
    combined_df = combined_df.sort_index(ascending=True)   # or ascending=False for reverse order

    # Write out
    combined_df.to_csv(output_path)
    print(f"Compiled U.S. averages saved to {output_path}")

if __name__ == "__main__":
    # Adjust this to your folder containing the CSVs
    input_dir = "_RuFaS Input Files/"
    # Desired output path for the compiled CSV
    output_csv = "_default_values.csv"
    compile_us_averages(input_dir, input_dir + output_csv)
