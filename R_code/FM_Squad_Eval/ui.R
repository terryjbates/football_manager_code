library(shiny)
library(ggplot2)

ui <- fluidPage(
  titlePanel("Football Manager Squad Evaluation"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput("attribute", 
                  "Select Player Attribute:", 
                  choices = colnames(data_df)[3:ncol(data_df)], 
                  selected = "Height"),
      sliderInput("n", "Number of Top Players:", min = 5, max = 30, value = 10),
      sliderInput("textSize", "Label Size:", min = 2, max = 10, value = 4, step = 0.5),
      checkboxInput("show_names", "Show Player Names", TRUE),
      # Add a checkbox group for player class filtering
      checkboxGroupInput("playerClass", 
                         label = "Select player classes to view", 
                         choices = c("Goalkeepers" = 0, 
                                     "Defenders" = 1,
                                     "Defensive Midfielders" = 2,
                                     "Central Midfielders" = 3,
                                     "Attacking Midfielders" = 4,
                                     "Forwards" = 5),
                         selected = 0:5) # Default all selected
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel("Coordinate Plot", plotOutput("coordinatePlot")),
        tabPanel("Scatter Plot", plotOutput("scatterPlot")),
        tabPanel("Bar Graph", plotOutput("barGraph")),
        tabPanel("Histogram", plotOutput("histogramPlot"))
      )
    )
  )
)
