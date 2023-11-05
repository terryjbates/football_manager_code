# Load required libraries
library(rvest)
library(tidyverse)

# Read the HTML file
html_file <- read_html("sample.html")

# Extract the table containing player data
table_data <- html_file %>%
  html_table(fill = TRUE)

# Initialize variables
best_pos_column <- NULL

# Iterate through all columns in the first row of the table
for (col_name in names(table_data[[1]][1, ])) {
  # Check if the column name contains "Best Pos" (case-insensitive)
  if (grepl("Best Pos", col_name, ignore.case = TRUE)) {
    best_pos_column <- col_name
    break
  }
}

# Check if "Best Pos" column is found
if (is.null(best_pos_column)) {
  print("Error: 'Best Pos' column not found.")
} else {
  # Extract "Best Pos" values
  best_pos_values <- table_data[[1]][, best_pos_column]
  
  # Create a data frame for "Best Pos" values
  pos_df <- data.frame(Best_Pos = best_pos_values)
  
  # Define the mapping of "Position Coordinate: Positions"
  position_mapping <- list(
    "2.5,0" = ("GK"),
    "0,1" = c("D(L)", "D(LC)","D/WB (RL)", "D/WB (L)"),
    "1,1" = c("CD", "NCB", "BPD", "L"),
    "2,1" = c("CD", "NCB", "BPD", "L"),
    "3,1" = c("CD", "NCB", "BPD", "L"),
    "4,1" =  c("D(L)", "D(LC)","D/WB (RL)", "D/WB (L)"),
    "0,2" = c("WB", "CWB", "IWB"),
    "1,2" = c("DM", "DLP", "A", "HB", "REG", "RPM"),
    "2,2" = c("DM", "DLP", "A", "HB", "REG", "RPM"),
    "3,2" = c("DM", "DLP", "A", "HB", "REG", "RPM"),
    "4,2" = c("WB", "CWB", "IWB"),
    "0,3" = c("DW", "W", "IW", "WM"),
    "1,3" = c("CM", "RPM", "AP", "DLP", "BBM", "MEZ"),
    "2,3" = c("CM", "RPM", "AP", "DLP", "BBM", "MEZ"),
    "3,3" = c("CM", "RPM", "AP", "DLP", "BBM", "MEZ"),
    "4,3" = c("DW", "W", "IW", "WM"),
    "0,4" = c("RAM", "W", "IW", "IF", "AP"),
    "1,4" = c("AP", "AM", "SS", "T", "ENG"),
    "2,4" = c("AP", "AM", "SS", "T", "ENG"),
    "3,4" = c("AP", "AM", "SS", "T", "ENG"),
    "4,4" = c("RAM", "W", "IW", "IF", "AP"),
    "1.5,5" = c("ST (C)"),
    "2,5" = c("ST (C)"),
    "3.5,5" = c("ST (C)")
  )
  
  # Function to map positions to coordinates
  map_positions_to_coordinates <- function(positions, mapping) {
    coordinates <- character(length(positions))
    for (i in seq_along(positions)) {
      pos <- positions[i]
      matched_coordinates <- sapply(mapping, function(x) pos %in% x)
      match <- names(matched_coordinates)[which(matched_coordinates)]
      coordinates[i] <- match
    }
    return(coordinates)
  }
  
  
  # Function to map positions to coordinates
  map_positions_to_coordinates <- function(positions, mapping) {
    coordinates <- character(length(positions))
    for (i in seq_along(positions)) {
      pos <- positions[i]
      matched_coordinates <- sapply(mapping, function(x) pos %in% x)
      match <- names(matched_coordinates)[which(matched_coordinates)]
      coordinates[i] <- match
    }
    return(coordinates)
  }
  
  # Map "Best Pos" values to coordinates
  coordinates <- map_positions_to_coordinates(best_pos_values, position_mapping)
  
  # Create a data frame for plotting
  squad_depth_df <- data.frame(Coordinates = coordinates)
  
  # Count the frequency of each coordinate
  pos_counts <- table(squad_depth_df$Coordinates)
  
  # Add frequency to the data frame
  squad_depth_df$Frequency <- as.numeric(pos_counts[match(squad_depth_df$Coordinates, names(pos_counts))])
  
  # Create a gradient color scale for the plot
  gradient_colors <- scale_fill_gradient(low = "red", high = "green")
  
  # Create the plot using ggplot
  ggplot(data = squad_depth_df, aes(x = 1, y = Coordinates, fill = Frequency)) +
    geom_tile() +
    gradient_colors +
    labs(title = "Squad Depth Visualization", x = "", y = "Position") +
    theme_void() +
    theme(legend.position = "bottom")
}
