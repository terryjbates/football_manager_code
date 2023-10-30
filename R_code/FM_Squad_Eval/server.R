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
  
  # Player class mapping
  player_class <- list(
    `0` = c("Goalkeepers"),
    `1` = c("Defenders"),
    `2` = c("Defensive Midfielders"),
    `3` = c("Central Midfielders"),
    `4` = c("Attacking Midfielders"),
    `5` = c("Forwards")
  )
  
  
  player_class_df <- stack(player_class)
  colnames(player_class_df) <- c("Class", "Y")
  player_class_df$Y <- as.character(player_class_df$Y)
  
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
    # Merge the map_df with the data_df to get the coordinates
    merged_df <- left_join(data_df, map_df, by = "Best_Pos")
    
    # Join with the player class mapping
    merged_df <- left_join(merged_df, player_class_df, by = "Y")
    
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- merged_df %>% filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(
      need(nrow(filtered_df) > 0, "Please select one or more player classes to view.")
    )
    
    # Extract last names
    last_names <- sapply(strsplit(filtered_df$Name, " "), function(x) tail(x, 1))
    
    # Create a label for each player with their last name and the selected attribute
    selected_attribute <- filtered_df[[input$attribute]]
    filtered_df$label <- paste0(last_names, "\n", selected_attribute)
    
    # Convert X and Y columns to numeric
    filtered_df$X <- as.numeric(filtered_df$X)
    filtered_df$Y <- as.numeric(filtered_df$Y)
    
    # Calculate label offsets for radial distribution
    filtered_df <- filtered_df %>%
      group_by(X, Y) %>%
      mutate(num_labels = n(),
             angle = row_number() * (2 * pi / num_labels),
             x_offset = ifelse(is.na(X), 0, 0.3 * cos(angle)), # Adjust 0.3 for desired label distance
             y_offset = ifelse(is.na(Y), 0, 0.3 * sin(angle))) %>%
      ungroup()
    
    # Plot
    ggplot(data = filtered_df, aes(x = as.numeric(X), y = as.numeric(Y))) +
      geom_point(aes(color = as.factor(Best_Pos)), size = 3) +
      theme_minimal() +
      theme(legend.position = "none") +
      labs(title = "Squad Depth") +
      geom_text(aes(x = X + x_offset, y = Y + y_offset, label =  gsub("Player ", "", Name)), size = input$textSize) +
      ylim(-1,6) +
      xlim(-3,3)
  })
  
  # Scatter Plot
  output$scatterPlot <- renderPlot({
    # Filter based on selected classes
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- data_df %>% 
      left_join(map_df, by = "Best_Pos") %>% 
      left_join(player_class_df, by = "Y") %>% 
      filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(
      need(nrow(filtered_df) > 0, "Please select one or more player classes to view.")
    )
    
    ggplot(filtered_df, aes(x = Weight , y = Height)) +
      geom_point(aes(color = filtered_df[[input$attribute]]), size = 4) +
      theme_minimal() +
      geom_text_repel(aes(label =  gsub("Player ", "", Name)), box.padding = unit(0.5, "lines"), size = input$textSize) +
      labs(color = input$attribute)
  })
  
  # Bar Graph
  output$barGraph <- renderPlot({
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- data_df %>% 
      left_join(map_df, by = "Best_Pos") %>% 
      left_join(player_class_df, by = "Y") %>% 
      filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(
      need(nrow(filtered_df) > 0, "Please select one or more player classes to view.")
    )
    
    top_players <- head(filtered_df[order(-filtered_df[[input$attribute]]), ], n = input$n)
    ggplot(top_players, aes(x = reorder(gsub("Player ", "", Name), -filtered_df[[input$attribute]]), y = filtered_df[[input$attribute]])) +
      geom_bar(stat = "identity") +
      theme_minimal() +
      coord_flip() +
      labs(y = input$attribute, x = 'Name')
  })
  
  # Histogram
  output$histogramPlot <- renderPlot({
    # Filter based on selected classes
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- data_df %>% 
      left_join(map_df, by = "Best_Pos") %>% 
      left_join(player_class_df, by = "Y") %>% 
      filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(
      need(nrow(filtered_df) > 0, "Please select one or more player classes to view.")
    )
    
    ggplot(filtered_df, aes(x = filtered_df[[input$attribute]])) +
      geom_histogram(binwidth = 5) +
      theme_minimal() +
      labs(x = input$attribute)
  })
}