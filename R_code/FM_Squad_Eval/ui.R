#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#
# ui.R
library(shiny)

# Define the UI
shinyUI(
  fluidPage(
    titlePanel("Dynamic Player Visualization"),
    
    # Sidebar layout with input and output definitions
    sidebarLayout(
      
      # Inputs
      sidebarPanel(
        # Dropdown for selecting attribute
        selectInput("attribute", "Choose an attribute:", 
                    choices = c("Height", "Morale", "ACC"), 
                    selected = "Height"),
        
        # Slider for point size
        sliderInput("pointSize", "Point Size:", min = 1, max = 5, value = 3),
        
        # Checkbox for displaying names
        checkboxInput("showNames", "Display Player Names", TRUE)
      ),
      
      # Output
      mainPanel(
        plotOutput("playerPlot")
      )
    )
  )
)
