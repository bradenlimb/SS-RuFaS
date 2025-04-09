#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:07:53 2025

@author: bradenlimb
"""
#%% Import Modules
import os
import pandas as pd
from tqdm import tqdm

#%% Input and Output Directories
# === Settings ===
input_dir = "_RuFaS Input Files Wrong Units"
output_dir = "_RuFaS Input Files Correct Units"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)
# asdf
#%% Dictionary of files and conversion factors
# === Dictionary format: 'old_file.csv': ('new_file.csv', conversion_factor) ===
file_map = {
    # "cattle_calves-price-received_dollar-per-cwt.csv": ("commodity_prices.calves_all.dollar_per_kilogram.csv", 'cwt_to_kg'),
    # "cattle_cows-milk-price-received_dollar-per-head.csv": ("commodity_prices.cows_milk.dollar_per_animal.csv", 'none'),
    # "cattle_cows-price-received_dollar-per-cwt.csv": ("commodity_prices.cows_all.dollar_per_kilogram.csv", 'cwt_to_kg'),
    # "cattle_GE-500-price-received_dollar-per-cwt.csv": ("commodity_prices.cows_ge_500.dollar_per_kilogram.csv", 'cwt_to_kg'),
    # "cattle_steers-and-heifers-GE-500-price-received_dollar-per-cwt.csv": ("commodity_prices.cows_steers_and_heifers_ge_500.dollar_per_kilogram.csv", 'cwt_to_kg'),
    
    # "crops_corn-grain-price-recieved_dollar-per-bushel.csv": ("commodity_prices.corn_grain.dollar_per_kilogram.csv", 'bushel-corn_to_kg'),
    # "crops_corn-silage-price-recieved_dollar-per-ton.csv": ("commodity_prices.corn_silage.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    
    # "crops_hay-alfalfa-price-received_dollar-per-ton.csv": ("commodity_prices.alfalfa_hay.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "crops_hay-excluding-alfalfa-price-received_dollar-per-ton.csv": ("commodity_prices.hay_excluding_alfalfa.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "crops_hay-price-received_dollar-per-ton.csv": ("commodity_prices.hay_all.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    
    # "crops_rye-price-received_dollar-per-bushel.csv": ("commodity_prices.rye_grain.dollar_per_kilogram.csv", 'bushel-corn_to_kg'), # Bushel of rye is the same weight as corn
    
    # "crops_soybean-price-received_dollar-per-bushel.csv": ("commodity_prices.soybean_grain.dollar_per_kilogram.csv", 'bushel-soy_to_kg'), 
    # "crops_soybean-meal-price-recieved_dollar-per-ton.csv": ("commodity_prices.soybean_meal.dollar_per_kilogram.csv", 'ton-metric_to_kg'), 
    
    "crops_winter-wheat-price-received_dollar-per-bushel.csv": ("commodity_prices.winter_wheat_grain.dollar_per_kilogram.csv", 'bushel-soy_to_kg'), # Bushel of winter wheat is the same weight as soybeans
    
    # "diesel_retail_dollar-per-gallon.csv": ("commodity_prices.diesel.dollar_per_liter.csv", 'gallon_to_liter'),
    # "gasoline_retail_dollar-per-gallon.csv": ("commodity_prices.gasoline.dollar_per_liter.csv", 'gallon_to_liter'),
    
    # "electricity_commercial_dollar-per-kwh.csv": ("commodity_prices.elec_commercial.dollar_per_kwh.csv", 'none'),
    # "electricity_industrial_dollar-per-kwh.csv": ("commodity_prices.elec_industrial.dollar_per_kwh.csv", 'none'),
    # "electricity_residential_dollar-per-kwh.csv": ("commodity_prices.elec_residential.dollar_per_kwh.csv", 'none'),
    
    # "feeds_alfalfa-silage_dollar-per-ton.csv": ("commodity_prices.alfalfa_silage.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "feeds_almond-hulls_dollar-per-ton.csv": ("commodity_prices.almond_hulls.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "feeds_barley-silage_dollar-per-ton.csv": ("commodity_prices.barley_silage.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "feeds_calcium-phosphate-di_dollar-per-kg.csv": ("commodity_prices.calcium_phosphate_di.dollar_per_kilogram.csv", 'none'),
    # "feeds_calf-starter-18CP_dollar-per-kg.csv": ("commodity_prices.calf_starter_18cp.dollar_per_kilogram.csv", 'none'),
    # "feeds_limestone_dollar-per-kg.csv": ("commodity_prices.limestone.dollar_per_kilogram.csv", 'none'),
    # "feeds_sudan-silage_dollar-per-ton.csv": ("commodity_prices.sundan_silage.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    
    # "feeds_milk-price-received_dollar-per-CWT.csv": ("commodity_prices.milk.dollar_per_liter.csv", 'cwt-milk_to_liters'),
    # "feeds_milk-whole_dollar-per-gallon.csv": ("commodity_prices.milk_retail.dollar_per_liter.csv", 'gallon_to_liter'),
    
    # "labor_hired-wage-rate_dollar-per-hour.csv": ("farm_services.labor_hours.dollar_per_hour.csv", 'none'),
    
    # "natural-gas_commercial_dollar-per-mcf.csv": ("commodity_prices.natgas_commercial.dollar_per_megajoule.csv", 'mcf-natgas_to_mj'),
    # "natural-gas_industrial_dollar-per-mcf.csv": ("commodity_prices.natgas_industrial.dollar_per_megajoule.csv", 'mcf-natgas_to_mj'),
    # "natural-gas_residential_dollar-per-mcf.csv": ("commodity_prices.natgas_residential.dollar_per_megajoule.csv", 'mcf-natgas_to_mj'),
    
    # "propane_residential_dollar-per-gallon.csv": ("commodity_prices.propane_residential.dollar_per_liter.csv", 'gallon_to_liter'),
    # "propane_wholesale_dollar-per-gallon.csv": ("commodity_prices.propane_wholesale.dollar_per_liter.csv", 'gallon_to_liter'),
    
    # "water_irrigation_dollar-per-acre-foot.csv": ("commodity_prices.water_irrigation.dollar_per_cubic_meter.csv", 'acre-foot_to_cubic-meters'),
    # "water_retail_dollar-per-kgal.csv": ("commodity_prices.water_municipal.dollar_per_cubic_meter.csv", 'kgallon_to_cubic-meters'),
    
    # "fertilizer_nitrogen_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_nitrogen.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_phosphorus_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_phosphorus.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_potassium_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_potassium.dollar_per_kilogram.csv", 'ton-short_to_kg'),

    # "fertilizer_ammonium-nitrate_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_ammonium_nitrate.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_anhydrous-ammonia_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_anhydrous_ammonia.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_diammonium-phosphate-18-46-0_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_diammonium_phosphate.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_nitrogen-solutions-30pct_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_nitrogen_solutions_30pct.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_potassium-chloride-60pct-potassium_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_potassium_chloride.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_sulfate-of-ammonium_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_sulfate_of_ammonium.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_super-phosphate-20pct-phosphate_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_super_phosphate_20pct.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_super-phosphate-44to46pct-phosphate_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_super_phosphate_44to46pct.dollar_per_kilogram.csv", 'ton-short_to_kg'),
    # "fertilizer_urea-44to46pct-nitrogen_dollar-per-shortton.csv": ("commodity_prices.net_fertilizer_urea.dollar_per_kilogram.csv", 'ton-short_to_kg'),  
    
}

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

#%% Function
# === Function to apply conversion and save ===
def convert_csv_file(old_path, new_path, factor_name):
    # Read raw data without parsing types yet
    df = pd.read_csv(old_path, header=None, dtype=str)
    
    # Find conversion factor
    factor = conversion_factors[factor_name]

    # Convert all values except first row and first column
    for row in range(1, df.shape[0]):
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

    df.to_csv(new_path, index=False, header=False, float_format="%.6g")

#%% Loop
# === Loop through file_map and process ===
for original_name, (new_name, factor) in tqdm(file_map.items()):
    old_path = os.path.join(input_dir, original_name)
    new_path = os.path.join(output_dir, new_name)

    if os.path.exists(old_path):
        convert_csv_file(old_path, new_path, factor)
        print(f"Converted '{original_name}' -> '{new_name}' with factor {factor}")
    else:
        print(f"File not found: {original_name}")