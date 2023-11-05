library(shiny)
library(ggplot2)
library(dplyr)
library(tidyr)
library(ggrepel)
library(plotly)

function(input, output, session) {
  
  # Use reactiveVal to keep track of the toggle state
  toggleState <- reactiveVal(TRUE)
  
  # Observe the toggle button and invert the toggle state each time it is pressed
  observeEvent(input$toggleOrder, {
    toggleState(!toggleState())
  })
  
  
    # Add truncation function
  truncate_text <- function(text, maxlen = 8) {
    ifelse(nchar(text) > maxlen, paste0(substr(text, 1, maxlen - 3), "."), text)
  }
  
  
  player_class_df <- stack(player_class)
  colnames(player_class_df) <- c("Class", "Y")
  player_class_df$Y <- as.character(player_class_df$Y)
  
  # Invert the position_mapping_default
  inverted_mapping <-
    lapply(names(position_mapping_default), function(name) {
      positions <- position_mapping_default[[name]]
      setNames(rep(name, length(positions)), positions)
    }) %>% do.call(c, .)
  
  # Convert this list to a data.frame
  map_df <- data.frame(
    Best_Pos = names(inverted_mapping),
    Coordinate = inverted_mapping,
    stringsAsFactors = FALSE
  )
  
  # Split the coordinate into X and Y
  map_df <- tidyr::separate(map_df, Coordinate, c("X", "Y"), ",")
  
  # Create multiple plots if we have more than one Club
  output$dynamicCoordinatePlots <- renderUI({
    # Check if Club column exists
    if ("Club" %in% names(data_df) &&
        length(unique(data_df$Club)) > 1) {
      # Create a separate plot for each club
      plot_output_list <-
        lapply(unique(data_df$Club), function(club_name) {
          plot_output_id <- paste0("plot_", club_name)
          
          plotOutput(plot_output_id, height = "400px", width = "100%")
          
        })
      
      do.call(tagList, plot_output_list)
      
    } else {
      plotOutput("coordinatePlot", height = "400px", width = "100%")
    }
    
  })
  
  # Create a reactive expression for the coordinate plot
  output$coordinatePlot <- renderPlot({
    # Merge the map_df with the data_df to get the coordinates
    # Then sort and filter the top n players
    top_n_players <-
      data_df %>% arrange(desc(get(input$attribute))) %>% head(n = input$n)
    merged_df <-
      left_join(top_n_players,
                map_df,
                by = "Best_Pos",
                relationship = "many-to-many")
    
    
    # Join with the player class mapping
    merged_df <- left_join(merged_df, player_class_df, by = "Y")
    
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- merged_df %>% filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(need(
      nrow(filtered_df) > 0,
      "Please select one or more player classes to view."
    ))
    
    # Extract last names
    last_names <-
      sapply(strsplit(filtered_df$Name, " "), function(x)
        tail(x, 1))
    
    # Create a label for each player with their last name and the selected attribute
    selected_attribute <- filtered_df[[input$attribute]]
    filtered_df$label <-
      paste0(last_names, "\n", selected_attribute)
    
    # Convert X and Y columns to numeric
    filtered_df$X <- as.numeric(filtered_df$X)
    filtered_df$Y <- as.numeric(filtered_df$Y)
    
    # Calculate label offsets for radial distribution
    filtered_df <- filtered_df %>%
      group_by(X, Y) %>%
      mutate(
        num_labels = n(),
        angle = row_number() * (2 * pi / num_labels),
        x_offset = ifelse(is.na(X), 0, 0.3 * cos(angle)),
        # Adjust 0.3 for desired label distance
        y_offset = ifelse(is.na(Y), 0, 0.3 * sin(angle))
      ) %>%
      ungroup()
    
    # Calculate descriptive statistics
    mean_val <- mean(top_n_players[[input$attribute]], na.rm = TRUE)
    median_val <-
      median(top_n_players[[input$attribute]], na.rm = TRUE)
    min_val <- min(top_n_players[[input$attribute]], na.rm = TRUE)
    max_val <- max(top_n_players[[input$attribute]], na.rm = TRUE)
    
    
    if (input$viewType == "2D") {
      # Plot single coordinate plot
      ggplot(data = filtered_df, aes(x = as.numeric(X), y = as.numeric(Y))) +
        geom_point(aes(color = as.factor(Best_Pos)), size = 3) +
        theme_minimal() +
        theme(legend.position = "none") +
        labs(title = "Squad Depth") +
        #geom_text(aes(x = X + x_offset, y = Y + y_offset, label =  truncate_text(gsub("Player ", "", Name))     ), size = input$textSize) +
        geom_text(aes(
          x = X + x_offset,
          y = Y + y_offset,
          label = label
        ),
        size = input$textSize) +
        ylim(-1, 6) +
        xlim(-3, 3) +
        xlab("Touchline") +
        ylab("Byline") +
        geom_segment(aes(
          x = -1,
          y = -1,
          xend = 1,
          yend = -1
        ), size = 1.5) + # Bottom horizontal
        geom_segment(aes(
          x = -1,
          y = -1,
          xend = -1,
          yend = 0
        ), size = 1.5) + # Left vertical
        geom_segment(aes(
          x = 1,
          y = -1,
          xend = 1,
          yend = 0
        ), size = 1.5) +   # Right vertical
        labs(
          title = paste0(
            "Squad Depth\nMean: ",
            round(mean_val, 2),
            " Median: ",
            round(median_val, 2),
            " Min: ",
            min_val,
            " Max: ",
            max_val
          )
        ) # Matches labs( title)
    }  else {
      # Calculate the mean value for the z-axis
      mean_val <-
        mean(as.numeric(filtered_df[[input$attribute]]), na.rm = TRUE)
      
      # Create a grid for the surface plane
      x_range <-
        seq(min(as.numeric(filtered_df$X)), max(as.numeric(filtered_df$X)), length.out = 10)
      y_range <-
        seq(min(as.numeric(filtered_df$Y)), max(as.numeric(filtered_df$Y)), length.out = 10)
      z_matrix <-
        matrix(
          mean_val,
          nrow = length(x_range),
          ncol = length(y_range),
          byrow = TRUE
        )
      
      # Convert X, Y columns to numeric
      filtered_df$X <- as.numeric(filtered_df$X)
      filtered_df$Y <- as.numeric(filtered_df$Y)
      filtered_df$Z <- as.numeric(filtered_df[[input$attribute]])
      
      # Calculate label offsets for radial distribution around each point
      filtered_df <- filtered_df %>%
        group_by(X, Y, Z) %>% # Group by position
        mutate(
          group_id = cur_group_id(),
          # Assign a group ID for unique grouping
          num_labels = n(),
          # Count number of labels per group
          angle = 2 * pi * (row_number() - 1) / num_labels,
          # Distribute angles in radians
          textpos_x = X + 0.1 * cos(angle),
          # Calculate X offset
          textpos_y = Y + 0.1 * sin(angle),
          # Calculate Y offset
          textpos_z = Z + 0.05 # Offset Z a little bit
        ) %>%
        ungroup()

      # Group data by X, Y, and Z, then concatenate the player names and attribute values
      hover_data <- filtered_df %>%
        group_by(X, Y, Z) %>%
        summarise(
          hover_text = paste("", Name, "Value:", get(input$attribute), collapse = "<br>"),
          .groups = 'drop' # This drops the grouping
        )
      
      # Join this hover_data back to the filtered_df to have a hover text for each point
      filtered_df <- filtered_df %>%
        left_join(hover_data, by = c("X", "Y", "Z"))
  
      # Create a color scale where:
      #  - Red represents Z values close to 0
      #  - Green represents Z values higher than the mean value
      color_scale <- list(
        c(0, "red"),               # Z = 0
        c(mean_val / max(filtered_df$Z), "yellow"), # Z = mean_val
        c(1, "green")              # Z = max
      )
      
                
      # Plot the 3D graph
      plot_ly(data = filtered_df) %>%
        add_trace(
          x = ~ X,
          y = ~ Y,
          z = ~ Z,
          type = "scatter3d",
          mode = 'markers',
          marker = list(
            size = 10,
            color = ~Z,             # Color depends on the Z value
            colorscale = color_scale, # Use the custom color scale
            colorbar = list(
              title = "Value",
              len = 0.5,
              thinkness = 10,
              x = 1.02,
              y = 0.5,
              titleside = "right",
              titlefont= list(size=8)
              ),
            cmin = 0,              # Minimum value for the color scale
            cmax = max(filtered_df$Z) # Maximum value for the color scale
            ),
          text = ~hover_text,
          hoverinfo = "text"
        ) %>%
        add_trace(
          x = ~ textpos_x,
          y = ~ textpos_y,
          z = ~ textpos_z,
          type = "scatter3d",
          mode = 'text',
          text = ~ paste(
            "",
            gsub("Player Name", "", Name),
            ":",
            get(input$attribute)
          ),
          hoverinfo = "text",
          textposition = "top center"
        ) %>%
        # Add the mean value plane
        add_surface(
          x = ~ x_range,
          y = ~ y_range,
          z = ~ z_matrix,
          showscale = FALSE,
          opacity = 0.5,
          color = c('rgba(205, 205, 205, 0.5)'),
          name = "Mean Value Plane"
        ) %>%
        layout(scene = list(
          xaxis = list(title = "GoalMouth"),
          yaxis = list(title = "Byline"),
          zaxis = list(
            title = input$attribute,
            range = c(min(as.numeric(filtered_df[[input$attribute]])), max(as.numeric(filtered_df[[input$attribute]])))
          ),
          annotations = list(
            x = mean(x_range),
            y = mean(y_range),
            z = mean_val,
            text = paste("Mean:", round(mean_val, 2)),
            showarrow = FALSE,
            yanchor = "bottom",
            xanchor = "center"
          )
        ))
      
    }
    
  })
  
  # Generate plots for each club dynamically
  observe({
    if ("Club" %in% names(data_df) &&
        length(unique(data_df$Club)) > 1) {
      lapply(unique(data_df$Club), function(club_name) {
        plot_output_id <- paste0("plot_", club_name)
        
        output[[plot_output_id]] <- renderPlot({
          # Get the top n players from this club
          top_n_players_club <-
            data_df[data_df$Club == club_name, ] %>% arrange(desc(get(input$attribute))) %>% head(n = input$n)
          club_df <- top_n_players_club
          club_df <- data_df[data_df$Club == club_name, ]
          
          # Your existing code for the coordinate plot with club_df in place of data_df
          # Merge the map_df with the club_df to get the coordinates
          merged_df <-
            left_join(club_df,
                      map_df,
                      by = "Best_Pos",
                      relationship = "many-to-many")
          
          # Join with the player class mapping
          merged_df <-
            left_join(merged_df, player_class_df, by = "Y")
          
          selected_classes <-
            unlist(player_class[input$playerClass])
          filtered_df <-
            merged_df %>% filter(Class %in% selected_classes)
          
          # Validate that filtered_df has some rows
          validate(need(
            nrow(filtered_df) > 0,
            "Please select one or more player classes to view."
          ))
          
          # Extract last names
          last_names <-
            sapply(strsplit(filtered_df$Name, " "), function(x)
              tail(x, 1))
          
          # Create a label for each player with their last name and the selected attribute
          selected_attribute <- filtered_df[[input$attribute]]
          filtered_df$label <-
            paste0(last_names, "\n", selected_attribute)
          
          # Convert X and Y columns to numeric
          filtered_df$X <- as.numeric(filtered_df$X)
          filtered_df$Y <- as.numeric(filtered_df$Y)
          
          # Calculate label offsets for radial distribution
          filtered_df <- filtered_df %>%
            group_by(X, Y) %>%
            mutate(
              num_labels = n(),
              angle = row_number() * (2 * pi / num_labels),
              x_offset = ifelse(is.na(X), 0, 0.3 * cos(angle)),
              # Adjust 0.3 for desired label distance
              y_offset = ifelse(is.na(Y), 0, 0.3 * sin(angle))
            ) %>%
            ungroup()
          
          # Calculate descriptive statistics
          mean_val <-
            mean(top_n_players_club[[input$attribute]], na.rm = TRUE)
          median_val <-
            median(top_n_players_club[[input$attribute]], na.rm = TRUE)
          min_val <-
            min(top_n_players_club[[input$attribute]], na.rm = TRUE)
          max_val <-
            max(top_n_players_club[[input$attribute]], na.rm = TRUE)
          
          # Plot club-specific coordinate plot
          ggplot(data = filtered_df, aes(x = as.numeric(X), y = as.numeric(Y))) +
            geom_point(aes(color = as.factor(Best_Pos)), size = 3) +
            theme_minimal() +
            theme(legend.position = "none") +
            labs(title = paste0(club_name, " Squad Depth")) +
            geom_text(aes(
              x = X + x_offset,
              y = Y + y_offset,
              label = label
            ),
            size = input$textSize) +
            ylim(-1, 6) +
            xlim(-3, 3) +
            xlab("Touchline") +
            ylab("Byline") +
            geom_segment(aes(
              x = -1,
              y = -1,
              xend = 1,
              yend = -1
            ), size = 1.5) + # Bottom horizontal
            geom_segment(aes(
              x = -1,
              y = -1,
              xend = -1,
              yend = 0
            ), size = 1.5) + # Left vertical
            geom_segment(aes(
              x = 1,
              y = -1,
              xend = 1,
              yend = 0
            ), size = 1.5)  +  # Right vertical
            labs(
              title = paste0(
                "Squad Depth\nMean: ",
                round(mean_val, 2),
                " Median: ",
                round(median_val, 2),
                " Min: ",
                min_val,
                " Max: ",
                max_val
              )
            )
          
        })
        
      })
      
    }
    
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
    validate(need(
      nrow(filtered_df) > 0,
      "Please select one or more player classes to view."
    ))
    
    ggplot(filtered_df, aes(x = Weight , y = Height)) +
      geom_point(aes(color = filtered_df[[input$attribute]]), size = 4) +
      theme_minimal() +
      geom_text_repel(
        aes(label =  gsub("Player ", "", Name)),
        box.padding = unit(0.5, "lines"),
        size = input$textSize
      ) +
      labs(color = input$attribute)
  })
  
  # Bar Graph
  output$barGraph <- renderPlot({
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- data_df %>%
      left_join(map_df, by = "Best_Pos", relationship = "many-to-many") %>%
      left_join(player_class_df, by = "Y") %>%
      filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(need(
      nrow(filtered_df) > 0,
      "Please select one or more player classes to view."
    ))
    
    # Group by the attribute value and concatenate player names with the same value
    grouped_players <- filtered_df %>%
      group_by_at(vars(input$attribute)) %>%
      summarize(Players = paste(Name, collapse = ", "), .groups = 'drop') %>%
      ungroup() %>%
      arrange(desc(.data[[input$attribute]]))
    
    # Select top n values (not necessarily players because there could be ties)
    top_values <- head(grouped_players, n = input$n)
    
    # Create the bar chart
    ggplot(top_values, aes_string(x = input$attribute, y = input$attribute)) +
      geom_bar(stat = "identity") +
      geom_text(aes(label = Players), vjust = -0.5, hjust=0.5) +
      theme_minimal() +
      coord_flip() +
      labs(y = input$attribute, x = 'Name') +
      theme(axis.text.y = element_text(hjust = 1))

  })
  
  # Histogram
  output$histogramPlot <- renderPlot({
    # Filter based on selected classes
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- data_df %>%
      left_join(map_df, by = "Best_Pos", relationship = "many-to-many") %>%
      left_join(player_class_df, by = "Y") %>%
      filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(need(
      nrow(filtered_df) > 0,
      "Please select one or more player classes to view."
    ))
    # Used to be x = filtered_df
    ggplot(filtered_df, aes(x = .data[[input$attribute]])) +
      geom_histogram(binwidth = 5) +
      theme_minimal() +
      labs(x = input$attribute)
  })
  
  # Mean Value Bar Graph
  output$meanValueBarGraph <- renderPlotly({
    # Filter based on selected classes
    selected_classes <- unlist(player_class[input$playerClass])
    filtered_df <- data_df %>%
      left_join(map_df, by = "Best_Pos", relationship = "many-to-many") %>%
      left_join(player_class_df, by = "Y") %>%
      filter(Class %in% selected_classes)
    
    # Validate that filtered_df has some rows
    validate(need(
      nrow(filtered_df) > 0,
      "Please select one or more player classes to view."
    ))
    
    # Get the mean values of numerical attributes
    numerical_attributes <- filtered_df %>%
      select_if(is.numeric) %>%
      summarise_all(mean, na.rm = TRUE) %>%
      pivot_longer(everything(), names_to = "Attribute", values_to = "MeanValue")
    
    numerical_attributes$Attribute <-
      factor(numerical_attributes$Attribute, levels = rev(unique(numerical_attributes$Attribute)))
    
    
    # Order the data based on the toggle state
    ordered_data <- if (toggleState()) {
      numerical_attributes %>% arrange(MeanValue)
    } else {
      numerical_attributes %>% arrange(desc(Attribute))
    }
    
    # Debug line
    # browser()
    # Create the bar chart
    p <-
      ggplot(ordered_data,
             aes(
               x =  reorder(Attribute, if (toggleState())
                 Attribute
                 else
                   MeanValue),
               y = MeanValue,
               fill = MeanValue,
               text = paste("<b>", Attribute, "</b>",  ": ", MeanValue)
             )) +
      geom_bar(stat = "identity") +
      scale_fill_gradient(low = "red", high = "green") +
      theme_minimal() +
      coord_flip() +
      labs(x = "Attribute", y = "Mean Value")
    
    # Convert to plotly object
    ggplotly(p, tooltip = "text") %>% layout(margin = list(l = 50, r = 50, b = 100, t = 100, pad = 4))
  })
}