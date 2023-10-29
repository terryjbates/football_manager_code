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
  
  `-2,2` = c("D/WB (L)"),
  `-1,2` = c("DM"),
  `0,2` = c("DM"),
  `1,2` = c("DM"),
  `2,2` = c("D/WB (R)"),
  
  `-2,3` = c("M/AM (L)"),
  `-1,3` = c("M (C)"),
  `0,3` = c("M (C)"),
  `1,3` = c("M (C)"),
  `2,3` = c("M/AM (R)"),
  
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
  
  # Plot
  plot <- ggplot(data = merged_df, aes(x = X, y = Y)) +
    ggtitle("Squad Depth") +
    geom_bin2d(aes(fill = ..count.. / total_unique_players), bins = 30) + 
    scale_fill_gradient(name = "Percentage of Total Players", 
                        labels = scales::percent_format(scale = 100),
                        low = "red", 
                        high = "green") +
    geom_point(aes(color = Best_Pos), size = 3, shape = 21, stroke = 1.5) +
    labs(color = "Position") +
    theme_minimal() +
    geom_text(data = coord_counts, aes(label = n), check_overlap = TRUE, vjust = -1)
  
  return(plot)
}