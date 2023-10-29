library(shiny)
library(ggplot2)
library(dplyr)
library(tidyr)


function(input, output) {
  # Position mapping
  position_mapping_default <- list(
    "LM" = c(1,0),
    "ST" = c(2,2), "CF" = c(2,2),
    "RM" = c(2,0),
    "CM" = c(1,1)
  )
  
  # Sample data_df
  data_df <- data.frame(
    Name = c("Player A", "Player B", "Player C", "Player D"),
    Best_Pos = c("LM", "ST", "RM", "CM"),
    Height = c(180, 190, 175, 185),
    Morale = c(80, 90, 75, 85),
    ACC = c(90, 85, 88, 78),
    stringsAsFactors = FALSE
  )
  
  # Create a reactive expression for the plot
  output$playerPlot <- renderPlot({
    
    # Use the input$attribute to get the selected attribute from the dropdown
    selected_attribute <- data_df[[input$attribute]]
    
    # Convert position_mapping_default to a dataframe for joining
    map_df <- as.data.frame(do.call(rbind, position_mapping_default))
    colnames(map_df) <- c("X", "Y")
    map_df$Best_Pos <- rownames(map_df)
    
    # Merge this mapping dataframe with the data_df to get the coordinates
    merged_df <- left_join(data_df, map_df, by = "Best_Pos")
    
    # Extract last names
    last_names <- sapply(strsplit(merged_df$Name, " "), function(x) tail(x, 1))
    
    # Create a label for each player with their last name and the selected attribute
    merged_df$label <- paste0(last_names, "\n", selected_attribute)
    
    # Plot
    ggplot(data = merged_df, aes(x = X, y = Y)) +
      geom_bin2d(aes(fill = ..count..), bins = 30) +
      scale_fill_gradient2(low = "red", mid = "blue", high = "green", midpoint = median(table(merged_df$Best_Pos))) +
      theme_minimal() +
      theme(legend.position = "none") +
      labs(title = "Squad Depth") +
      xlim(-2, 4)+
      ylim(-2, 4) +
#      geom_text(data = subset(merged_df, !is.na(Best_Pos)),
#                aes(label = ifelse(input$showNames, label, NULL)),
#                hjust = -0.1, 
#                vjust = 1.5,
#                size = input$pointSize,
#                angle = 45)
      geom_text(data = subset(merged_df, !is.na(Best_Pos) & input$showNames),
                aes(label = label),
                hjust = -0.1, 
                vjust = 1.5,
                size = input$pointSize,
                angle = 0)
    
  })
}
