#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 16:06:35 2026

@author: bradenlimb
"""

import pandas as pd
import numpy as np
import requests
from io import StringIO

# --- 1. Get annual CPI (U.S. average, all items, CPI-U) ---

def load_cpi_series():
    """
    Loads annual-average CPI(-U) values by year into a dict: {year: cpi}.
    Expects an HTML table with headers:
      Year | Annual Average CPI(-U) | Annual Percent Change
    like the Minneapolis Fed CPI page. [file:18][web:8]
    """
    url = "https://www.minneapolisfed.org/about-us/monetary-policy/inflation-calculator/consumer-price-index-1800-"  # [web:8]
    resp = requests.get(url)
    resp.raise_for_status()
    html = resp.text

    # read all tables on the page
    tables = pd.read_html(html)  # [file:18]
    cpi_df = None

    # find the table that has the expected columns
    for t in tables:
        cols = [str(c).strip() for c in t.columns]
        if ("Year" in cols and
            any("Annual Average Index" in c for c in cols)):
            cpi_df = t
            break

    if cpi_df is None:
        raise RuntimeError("Could not find CPI table on page.")

    # normalize column names
    cpi_df.columns = [str(c).strip() for c in cpi_df.columns]

    # identify the CPI column (it contains 'Annual Average CPI')
    cpi_col = [c for c in cpi_df.columns if "Annual Average Index" in c][0]

    # keep only Year and CPI
    cpi_df = cpi_df[["Year", cpi_col]].copy()
    cpi_df = cpi_df.rename(columns={cpi_col: "CPI"})

    # clean and convert types
    cpi_df["Year"] = pd.to_numeric(cpi_df["Year"], errors="coerce")
    cpi_df["CPI"] = (
        cpi_df["CPI"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    cpi_df["CPI"] = pd.to_numeric(cpi_df["CPI"], errors="coerce")

    cpi_df = cpi_df.dropna(subset=["Year", "CPI"])

    return dict(zip(cpi_df["Year"].astype(int), cpi_df["CPI"]))

cpi_by_year = load_cpi_series()

# --- 2. Helper to find nearest available year in row ---

def find_nearest_year_with_value(year, years_array, values_array):
    """
    Given a target year, and arrays of column years and row values,
    return (nearest_year, value_at_nearest_year) or (None, None) if none exist.
    """
    mask = ~np.isnan(values_array)
    if not mask.any():
        return None, None

    available_years = years_array[mask]
    available_values = values_array[mask]

    idx = np.argmin(np.abs(available_years - year))
    return int(available_years[idx]), available_values[idx]

# --- 3. Inflation-based fill function for a single row ---

def fill_row_with_cpi_scaling(row, year_cols, cpi_by_year):
    """
    For a 1D numpy array 'row' with NaNs for missing values, fill NaNs
    by scaling from the closest non-NaN year using CPI ratios.
    """
    values = row.astype(float).copy()
    for j, year in enumerate(year_cols):
        if np.isnan(values[j]):
            base_year, base_val = find_nearest_year_with_value(year, year_cols, values)
            if base_year is None:
                continue  # nothing to scale from in this row

            # Need CPI for both years
            if year not in cpi_by_year or base_year not in cpi_by_year:
                continue

            cpi_target = cpi_by_year[year]
            cpi_base = cpi_by_year[base_year]
            # Scale proportionally by CPI
            values[j] = base_val * (cpi_target / cpi_base)

    return values

# --- 4. Load your CSV, fill missing values, and save ---

# Adjust this path to your actual file location
in_path = "_RuFaS Input Files/_default_values.csv"
out_path = "_RuFaS Input Files/_default_values_fallback.csv"

df = pd.read_csv(in_path)

# Assume first column is an identifier and remaining columns are year labels
id_col = df.columns[0]
year_cols = df.columns[1:]

# Parse column names to years (int), skipping non-year columns if any
parsed_years = []
valid_indices = []
for idx, col in enumerate(year_cols):
    try:
        y = int(col)
        parsed_years.append(y)
        valid_indices.append(idx + 1)  # +1 because of id column
    except ValueError:
        parsed_years.append(None)

parsed_years = np.array([y for y in parsed_years if y is not None])

# Work on a copy
filled_df = df.copy()

# Only process columns whose names are valid years and exist in CPI
cols_to_process = [c for c in year_cols if c.isdigit() and int(c) in cpi_by_year]
year_array = np.array([int(c) for c in cols_to_process])

for i in range(len(filled_df)):
    row = filled_df.loc[i, cols_to_process].to_numpy(dtype=float)
    filled_values = fill_row_with_cpi_scaling(row, year_array, cpi_by_year)
    filled_df.loc[i, cols_to_process] = filled_values

filled_df.to_csv(out_path, index=False)
print(f"Saved filled CSV to {out_path}")
