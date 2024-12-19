# Braden Limb

# Clear the Environment Each Run
rm(list = ls())

# Set Working Directory to Current Folder
setwd(getSrcDirectory(function() {})[1])

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

# Load Excel metadata
metadata <- read_excel("input_metadata.xlsx")

# Import shapefiles (outside the loop to avoid reloading)
states_sf <- read_sf("us_states_shapefile/States_shapefile.shp")
counties_sf <- read_sf("us_counties_shapefile/USA_Counties.shp")

# Loop through each row in the metadata
for (i in 1:nrow(metadata)) {
  # Extract metadata for the current file
  filename <- metadata$filename[i]
  datatype <- metadata$datatype[i]
  subtype <- metadata$subtype[i]
  units <- metadata$units[i]
  
  # Read the CSV file
  data <- read.csv(
    paste0("../_RuFaS Input Files/", filename, ".csv"),
    check.names = FALSE,
    colClasses = c(fips = "character")
  )
  
  # Read the counties file to reset it
  counties_sf <- read_sf("us_counties_shapefile/USA_Counties.shp")
  
  # Create the output directory
  directory <- file.path("RuFaS Input Maps", datatype, subtype)
  if (!file.exists(directory)) {
    dir.create(directory, recursive = TRUE)
  }
  print(directory)
  
  # Extract year columns
  years <- names(data)[sapply(names(data), function(x) grepl("^[0-9]+$", x))]
  
  # Calculate the maximum value and scaling
  max_val_use <- max(data[sapply(data, is.numeric)], na.rm = TRUE)
  scale_val <- round(max_val_use / 7, 0)
  
  # Initialize progress bar for the current file
  pb <- txtProgressBar(min = 0, max = length(years), style = 3)
  
  # Loop through each year and create a figure
  for (j in seq_along(years)) {
    year <- years[j]
    
    # Perform the join
    counties_sf <- counties_sf %>%
      left_join(data %>% select(fips, year), by = c("FIPS" = "fips")) %>%
      mutate(year = ifelse(year == 0, NA, year))  # Set zero values to NA
    
    # Generate dynamic color bar breaks
    color_bar_breaks <- c(0.001, seq(scale_val, floor(max_val_use / scale_val) * scale_val + scale_val, scale_val))
    color_bar_labels <- as.character(c(0, color_bar_breaks[-1]))
    
    # Check if all values in the current year's column are NA
    all_na <- all(is.na(counties_sf[[year]]))
    
    # If all values are NA, render a gray map
    if (all_na) {
      counties_sf[counties_sf$FIPS == "51013", year] <- 0.01
    }
    
    p <- ggplot() +
      geom_sf(data = states_sf, fill = "gray98", color = "black") +
      geom_sf(data = counties_sf, aes(fill = !!sym(year)), color = NA) +
      scale_fill_gradientn(
        colors = rev(brewer.pal(11, "RdYlGn")),
        na.value = "gray",
        limits = c(0.001, max_val_use),
        breaks = color_bar_breaks,
        labels = color_bar_labels
      ) +
      geom_sf(data = states_sf, fill = "NA", color = "black") +
      coord_sf(xlim = c(-125.3, -66.4), ylim = c(24, 49.9)) +
      labs(
        x = 'Longitude',
        y = 'Latitude',
        fill = paste0(year, " ", datatype, " Costs - ", subtype, " (", units, ")")
      ) +
      guides(fill = guide_colourbar(barwidth = 30, barheight = 1.5, direction = "horizontal", title.position = "top")) +
      theme_minimal() +
      theme(
        legend.position = "bottom",
        text = element_text(size = 12),
        axis.title = element_text(size = 12),
        axis.text = element_text(size = 12),
        legend.title = element_text(size = 12),
        legend.text = element_text(size = 12),
        plot.title = element_text(size = 12)
      )
    
    # Save the plot
    ggsave(filename = paste0(directory, "/", year, ".jpg"), plot = p, width = 12, height = 8)
    
    # Update progress bar
    setTxtProgressBar(pb, j)
  }
  
  # Close the progress bar for the current file
  close(pb)
}