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

shinyUI(
  fluidPage(
    titlePanel("Dynamic Player Attributes Visualization"),
    
    sidebarLayout(
      sidebarPanel(
        selectInput("attribute", "Choose an attribute:", 
                    choices = c("Height", "Morale", "ACC"))
      ),
      
      mainPanel(
        plotOutput("playerPlot")
      )
    )
  )
)
