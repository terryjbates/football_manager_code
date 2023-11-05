# Load necessary libraries
library(tidyverse)
library(rvest)
library(dplyr)
library(ggplot2)

source('./expand_positions.R')
source('./plot_positions.R')
# Read the HTML file
html_file <- "sample.html"
webpage <- read_html(html_file)

# Extract the table
player_table <- html_nodes(webpage, "table") %>% html_table(fill = TRUE)

# Convert the table to a data frame
player_data <- player_table[[1]]

# Change `Best Pos` to Best_Pos 
player_data <- player_data %>% mutate(Best_Pos = `Best Pos`)
  
# Create expanded dataframe. Preserves current values and generates
# added elements to data frame with unique `Best Pos`
expanded_df <- expand_positions(player_data)

# Plot the grid with squad depth
plot_positions(expanded_df)



# Test  data
#player_data <- data.frame(
#  Name = c("Player1", "Player2", "Player3"),
#  Best_Pos = c("D (RC), DM", "DM, M (C)", "D (RC), D (LC)")
#)

# Create a ggplot
#ggplot(position_counts, aes(x = reorder(Positions, -n), y = n, fill = Positions)) +
#  geom_bar(stat = "identity") +
#  geom_text(aes(label = n), vjust = -0.5, size = 4) +
#  theme_minimal() +
#  labs(x = "Position", y = "Count") +
#  coord_flip()
