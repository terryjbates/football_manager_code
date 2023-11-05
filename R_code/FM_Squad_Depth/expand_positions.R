library(dplyr)
library(tidyr)
source('plot_positions.R')

expand_positions <- function(player_data, position_mapping = position_mapping_default) {
  
  # Function to process the position
  process_pos <- function(pos) {
    # Check if pos contains parentheses with two or more letters
    if(grepl("\\(\\w{2,}\\)", pos)) {
      # Extract characters inside the parentheses
      chars_inside <- gsub(".*\\((\\w+)\\).*", "\\1", pos)
      # Create new positions for each character inside parentheses
      new_positions <- sapply(strsplit(chars_inside, NULL)[[1]], function(char) {
        gsub("\\(\\w+\\)", sprintf("(%s)", char), pos)
      })
      return(new_positions)
    } else {
      # Return as is
      return(pos)
    }
  }
  
  # Split and transform
  player_data_expanded <- player_data %>%
    separate_rows(Best_Pos, sep = ",\\s*") %>%
    rowwise() %>%
    mutate(Best_Pos = list(process_pos(Best_Pos))) %>%
    ungroup() %>%
    unnest(Best_Pos)
  
  # Remove duplicates
  player_data_unique <- player_data_expanded %>%
    group_by(Name) %>%
    distinct(Best_Pos, .keep_all = TRUE) %>%
    ungroup()
  
  # Identify the unique Best_Pos values that do not have a match in the lookup map
  unmatched_positions <- setdiff(unique(player_data_unique$Best_Pos), unlist(position_mapping))
  
  # Report these unmatched positions
  if (length(unmatched_positions) > 0) {
    cat("The following Best_Pos values in player_data_unique do not match any entry in the lookup map:\n")
    print(unmatched_positions)
  }
  
  return(player_data_unique)
}

# Sample data
#player_data <- data.frame(
#  Name = c("Player1", "Player2", "Player3"),
#  Best_Pos = c("D (RC), DM", "DM, M (C)", "D (RC), D (LC)")
#)

# Get the expanded positions
#expanded_df <- expand_positions(player_data)
#print(expanded_df)
