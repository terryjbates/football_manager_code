library(dplyr)
library(readr)
library(purrr)


suggest_tactical_style <- function(input_data) {
  # Load the tactical styles data
  tactical_styles_df <- read_csv("tactical_style_weightings.csv", show_col_types = FALSE)
  
  # Check for correct input type and columns
  if (!(is.data.frame(input_data) || is.list(input_data) || is_tibble(input_data)) ||
      !"Attribute" %in% names(input_data) || !"MeanValue" %in% names(input_data)) {
    stop("Input data must be a data frame, tibble or a list with 'Attribute' and 'MeanValue' columns.")
  }
  
  # Ensure that input is a data frame for easier manipulation
  input_data <- as.data.frame(input_data)
  
  # Normalize input to match the CSV format
  colnames(input_data)[colnames(input_data) == "Attribute"] <- "Style"
  
  # Calculate match scores for each tactical style
  scores <- sapply(tactical_styles_df$Style, function(style) {
    style_row <- tactical_styles_df[tactical_styles_df$Style == style, -ncol(tactical_styles_df)]
    sum(input_data$MeanValue * style_row[match(input_data$Style, names(style_row))])
  })
  
  # Get the top 3 matches
  top_matches <- head(sort(scores, decreasing = TRUE), 3)
  
  # Return the top 3 tactical style and formation combinations
  result <- lapply(names(top_matches), function(style) {
    formations <- tactical_styles_df$Formations[tactical_styles_df$Style == style]
    list(Style = style, Formations = formations)
  })
  
  return(result)
}



# Test the function
test_data <- tibble(Attribute = c("Det", "Pac", "Acc"),
                    MeanValue = c(2, 2.24, 2.32))

# Execute the function
result <- suggest_tactical_style(test_data)
print(result)
