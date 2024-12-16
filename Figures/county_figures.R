# Braden Limb

# Clear the Environment Each Run
rm(list = ls())

# Set Working Directory to Current Folder
setwd(getSrcDirectory(function(){})[1])

# Load Libraries
library(tidyr)
library(ggplot2)
library(gganimate)
library(dplyr)
library(ggmap)
library(sf)
library(RColorBrewer)
library(lubridate)
library(tools)
library(data.table)
library(terra)
library(readxl)

# Load the specified sheet
filename = 'natural-gas_industrial_dollar-per-mcf'
datatype = 'Natural Gas'
subtype = 'Industrial'
units = '$/MCF'

data <- read.csv(
  paste0("../_RuFaS Input Files/", filename, ".csv"),
  check.names = FALSE,
  colClasses = c(fips = "character")
)

# Check if the directory exists
directory <- file.path("RuFaS Input Maps",datatype, subtype)
if (!file.exists(directory)) {
  dir.create(directory, recursive = TRUE)
}

# Extract year column names (assuming they are all numeric)
years <- names(data)[sapply(names(data), function(x) grepl("^[0-9]+$", x))]

# Calculate the maximum value from the raster data, ignoring NA
max_val_use <- max(data[sapply(data, is.numeric)], na.rm = TRUE)
scale_val = ceiling(max_val_use/7)

# Import a geojson or shapefile
states_sf = read_sf("us_states_shapefile/States_shapefile.shp")
counties_sf = read_sf("us_counties_shapefile/USA_Counties.shp")

x_limits = c(-125.3, -66.4)
y_limits = c(24, 49.9)

# Create a color palette using RColorBrewer
color_palette <- rev(brewer.pal(11, "RdYlGn"))  # Example with "RdYlGn" palette, 11 colors

# Initialize progress bar
pb <- txtProgressBar(min = 0, max = length(years), style = 3)

# Loop through each year and create a figure
for (i in seq_along(years)) {
  year <- years[i]
  
  # Perform the join
  counties_sf <- counties_sf %>%
    left_join(data %>% select(fips, year), by = c("FIPS" = "fips"))
  
  # Set zero values to NA in the data frame to apply the gray color only to those values
  counties_sf <- counties_sf %>%
    mutate(year = ifelse(year == 0, NA, year))
  
  # Generate dynamic color bar breaks that scale by a factor of a specified values
  color_bar_breaks <- c(0.001, seq(scale_val,floor(max_val_use/scale_val)*scale_val+scale_val, scale_val))  # 0.001, 1, 3, 9, 27, ...
  color_bar_labels <- as.character(c(0, color_bar_breaks[-1]))  # Label "0" for the first break
  
  # # Create the directory for plots if it doesn't exist
  # current_path <- getwd()
  # current_folder <- basename(current_path)
  
  p <- ggplot() +
    geom_sf(data = states_sf, fill = "gray98", color = "black") + #https://www.nceas.ucsb.edu/sites/default/files/2020-04/colorPaletteCheatsheet.pdf
    geom_sf(data = counties_sf, color = "NA", aes(fill = !!sym(year))) +
    scale_fill_gradientn(colors = color_palette,
                         na.value = "gray",
                         limits = c(0.001, max_val_use),
                         breaks = color_bar_breaks,  # Manually set breaks
                         labels = color_bar_labels) +  # Custom labels, including "0"geom_sf(data = states_sf, fill = "NA", color = "black") + #https://www.nceas.ucsb.edu/sites/default/files/2020-04/colorPaletteCheatsheet.pdf
    geom_sf(data = states_sf, fill = "NA", color = "black") +
    coord_sf(xlim = x_limits, ylim = y_limits) +
    labs(
         x = 'Longitude',
         y = 'Latitude',
         fill = paste0(year, " ", datatype, " Costs - ", subtype,' (', units,')')) +
    guides(fill = guide_colourbar(barwidth = 30,
                                  barheight = 1.5,
                                  direction = "horizontal",
                                  title.position = "top")) +  # Adjust the barwidth and barheight as needed
    theme_minimal() +
    theme(legend.position = "bottom",
          text = element_text(size = 12),  # Overall text size
          axis.title = element_text(size = 12),  # Axis titles
          axis.text = element_text(size = 12),  # Axis text
          legend.title = element_text(size = 12),  # Legend title
          legend.text = element_text(size = 12),  # Legend text
          plot.title = element_text(size = 12)  # Plot title
    )
  
  ggsave(filename = paste0(directory,"/",year,".jpg", sep = ""), plot = p, width = 12, height = 8)
  
  # Update progress bar
  setTxtProgressBar(pb, i)
}
