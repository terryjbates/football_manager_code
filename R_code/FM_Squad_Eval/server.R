library(shiny)
library(ggplot2)
library(dplyr)
library(tidyr)
library(ggrepel)

function(input, output) {
  # Position mapping
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
  
  # Invert the position_mapping_default
  inverted_mapping <- lapply(names(position_mapping_default), function(name) {
    positions <- position_mapping_default[[name]]
    setNames(rep(name, length(positions)), positions)
  }) %>% do.call(c, .)
  
  # Convert this list to a data.frame
  map_df <- data.frame(Best_Pos = names(inverted_mapping), 
                       Coordinate = inverted_mapping, 
                       stringsAsFactors = FALSE)
  # Split the coordinate into X and Y
  map_df <- tidyr::separate(map_df, Coordinate, c("X", "Y"), ",")

  
    
  # Create a reactive expression for the coordinate plot
  output$coordinatePlot <- renderPlot({
    # Use the input$attribute to get the selected attribute from the dropdown
    selected_attribute <- data_df[[input$attribute]]
    
    # Merge the map_df with the data_df to get the coordinates
    merged_df <- left_join(data_df, map_df, by = "Best_Pos")
    
    # Extract last names
    last_names <- sapply(strsplit(merged_df$Name, " "), function(x) tail(x, 1))
    
    # Create a label for each player with their last name and the selected attribute
    merged_df$label <- paste0(last_names, "\n", selected_attribute)

    # Radially labeling
    # Calculate label offsets for radial distribution
    # Convert X and Y columns to numeric
    merged_df$X <- as.numeric(merged_df$X)
    merged_df$Y <- as.numeric(merged_df$Y)
    
    # Calculate label offsets for radial distribution
    merged_df <- merged_df %>%
      group_by(X, Y) %>%
      mutate(num_labels = n(),
             angle = row_number() * (2 * pi / num_labels),
             x_offset = ifelse(is.na(X), 0, 0.3 * cos(angle)), # Adjust 0.3 for desired label distance
             y_offset = ifelse(is.na(Y), 0, 0.3 * sin(angle))) %>%
      ungroup()
    
    
        
    # Plot
    ggplot(data = merged_df, aes(x = as.numeric(X), y = as.numeric(Y))) +
      geom_point(aes(color = as.factor(Best_Pos)), size = 3) +
      theme_minimal() +
      theme(legend.position = "none") +
      labs(title = "Squad Depth") +
      geom_text(aes(x = X + x_offset, y = Y + y_offset, label = label), size = input$textSize) +
      ylim(-1,6) +
      xlim(-3,3)
#      geom_text_repel(
#        aes(label = label),
#        nudge_x = 0.5,
#        nudge_y = 0.5,
#        segment.color = "transparent"
#      )
      
    
  })
  
  # Scatter Plot
  output$scatterPlot <- renderPlot({
    ggplot(data_df, aes(x = Weight , y = Height)) +
      geom_point(aes(color = data_df[[input$attribute]]), size = 4) +
      theme_minimal() +
      geom_text(aes(label =  gsub("Player ", "", Name)), vjust = -1, hjust = 1.5, size = input$textSize) +
      labs(color = input$attribute)
  })
  
  # Bar Graph
  output$barGraph <- renderPlot({
    top_players <- head(data_df[order(-data_df[[input$attribute]]), ], n = input$n)
    ggplot(top_players, aes(x = reorder(gsub("Player ", "", Name), -data_df[[input$attribute]]), y = data_df[[input$attribute]])) +
      geom_bar(stat = "identity") +
      theme_minimal() +
      coord_flip() +
      labs(y = input$attribute, x = 'Name') # Make x-axis make sense
  })
  
  # Histogram
  output$histogramPlot <- renderPlot({
    ggplot(data_df, aes(x = data_df[[input$attribute]])) +
      geom_histogram(binwidth = 5) +
      theme_minimal() +
      labs(x = input$attribute) # Make x-axis make sense
  })
}
