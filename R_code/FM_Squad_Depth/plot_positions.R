library(ggplot2)
library(viridis)
library(dplyr)

# Create position mapping
position_mapping_default <- list(
  `0,0` = c("GK"),
  `-2,1` = c("D (L)", "D/WB (L)"),
  `-1,1` = c("D (C)"),
  `0,1` = c("D (C)"),
  `1,1` = c("D (C)"),
  `2,1` = c("D (R)", "D/WB (R)"),
  
  `-2,2` = c("D/WB (L)", "WB (L)"),
  `-1,2` = c("DM"),
  `0,2` = c("DM"),
  `1,2` = c("DM"),
  `2,2` = c("D/WB (R)", "WB (R)"),
  
  `-2,3` = c("M/AM (L)", "M (L)"),
  `-1,3` = c("M (C)"),
  `0,3` = c("M (C)"),
  `1,3` = c("M (C)"),
  `2,3` = c("M/AM (R)", "M (R)"),
  
  `-2,4` = c("M/AM (L)", "AM (L)"),
  `-1,4` = c("AM (C)"),
  `0,4` = c("AM (C)"),
  `1,4` = c("AM (C)"),
  `2,4` = c("M/AM (R)", "AM (R)"),
  
  `-1,5` = c("ST (L)"),
  `0,5` = c("ST (C)"),
  `1,5` = c("ST (R)")
)
plot_positions <- function(data_df, position_mapping = position_mapping_default) {
  
  # Convert the list to a data frame
  map_df <- do.call(rbind, lapply(names(position_mapping), function(name) {
    data.frame(
      X = as.numeric(unlist(strsplit(name, ","))[1]),
      Y = as.numeric(unlist(strsplit(name, ","))[2]),
      Best_Pos = position_mapping[[name]]
    )
  }))
  
  # Expand this dataframe to have one row per "Best_Pos"
  map_df <- tidyr::unnest(map_df, cols = c(Best_Pos))
  
  # Merge this mapping dataframe with the data_df to get the coordinates
  merged_df <- left_join(data_df, map_df, by = "Best_Pos", relationship = "many-to-many")
  
  # Find the total number of unique players
  total_unique_players <- n_distinct(data_df$Name)
  
  # Precompute the counts for each coordinate
  coord_counts <- merged_df %>%
    group_by(X, Y) %>%
    tally() %>%
    ungroup()

  
  # Get unique positions and the associated shape codes
  unique_positions <- unique(as.character(merged_df$Best_Pos))
  shape_codes <- c(16, 17, 15, 3, 8, 24, 23, 0:25)  # add more shape codes if needed
  shape_codes <- shape_codes[1:length(unique_positions)]
  
  
  
  # Compute the total number of players
  total_players <- nrow(merged_df)
  
  # Calculate the counts for each (X, Y) combination
  counts_df <- merged_df %>%
    group_by(X, Y) %>%
    summarise(count = n())

  # Create LastName to create LastName label option
  merged_df$LastName <- sapply(strsplit(merged_df$Name, " "), tail, 1)
 
  # Radial Jitter section
  radius <- 0.25  # You can adjust this value to increase/decrease distance from the point
  
  # Compute the number of players for each coordinate
  count_data <- merged_df %>% group_by(X, Y) %>% summarise(n = n())
  
  # Join this back to merged_df
  merged_df <- left_join(merged_df, count_data)
  
  # Compute the angle for each player around their Best_Pos
  merged_df <- merged_df %>% group_by(X, Y) %>% mutate(angle = row_number() * (2*pi/n))
  
  # Calculate the new x and y offsets for the last names
  merged_df$label_x <- merged_df$X + radius * cos(merged_df$angle)
  merged_df$label_y <- merged_df$Y + radius * sin(merged_df$angle)
  
     
  plot <- ggplot(data = merged_df, aes(x = X, y = Y)) +

    # Points for each position
    geom_point(aes(color = Best_Pos), size = 3) +
    
    # For the heatmap
    geom_bin2d(aes(fill = after_stat(count)), bins = 30) +

    # Position label below the point
    geom_text(aes(label = Best_Pos), size = 2.5, vjust = 2.5, hjust = 0.5) +

    # Jitter the player names around their Best_Pos
    #geom_text(aes(label = Name), position = position_jitter(width = 0.3, height = 0.3), size = 2.5, alpha = 0.7) +
    #geom_text(aes(label = LastName), position = position_jitter(width = 0.3, height = 0.3), size = 2.5, alpha = 0.7) +

    # Place the player last names radially around their Best_Pos
    geom_text(aes(x = label_x, y = label_y, label = LastName), size = 2.5, alpha = 0.7) +

    # Count of players at each position using counts_df
    geom_text(data = counts_df, aes(label = count), vjust = -1, hjust = 0.5, size = 2.5, color = "black") +

    # Adjusted gradient scale for clarity
    scale_fill_gradient(name = "Number of Players", low = "red", high = "green") +

    theme_minimal() +
    labs(title = "Squad Depth") +
    
    # Additional theme customization to remove the unwanted legends
    theme(legend.position = "bottom") +
    guides(color=FALSE)

  return(plot)
}
