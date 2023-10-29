# server.R

library(shiny)
library(ggplot2)
# Load other required libraries here...

function(input, output) {
  
  output$playerPlot <- renderPlot({
    # Sample data (replace with your actual data)
    data_df <- data.frame(
      Name = c("John Doe", "Jane Smith", "Robert Brown"),
      Best_Pos = c("4,4", "3,3", "2,2"),
      Height = c("6'2\"", "5'7\"", "6'0\""),
      Morale = c("High", "Medium", "Low"),
      ACC = c(85, 90, 78)
    )
    
    # Extracting X and Y for plotting
    data_df$X <- as.numeric(unlist(lapply(strsplit(data_df$Best_Pos, ","), "[[", 1)))
    data_df$Y <- as.numeric(unlist(lapply(strsplit(data_df$Best_Pos, ","), "[[", 2)))

    # Create LastName to create LastName label option
    data_df$LastName <- sapply(strsplit(data_df$Name, " "), tail, 1)
    
        
    # Combine Name and selected attribute for labeling
    #data_df$label <- paste(data_df$Name, data_df[[input$attribute]])
    data_df$label <- paste(data_df$LastName, data_df[[input$attribute]])
    # Plotting
    ggplot(data_df, aes(x = X, y = Y)) +
      geom_bin2d(aes(fill = ..count..)) +
      scale_fill_gradient(name = "No. of Players", low = "white", high = "red") +
      geom_text(aes(label = label), hjust = -0.5, vjust = 1.5) +
      labs(title = "Dynamic Player Attributes Visualization") +
      # Include other aesthetics or themes as required
      coord_cartesian(xlim = c(min(data_df$X) - 1, max(data_df$X) + 2), ylim = c(min(data_df$Y) - 1, max(data_df$Y) + 1))
  })
}
