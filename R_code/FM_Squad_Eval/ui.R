library(shiny)
library(ggplot2)
library(plotly)

ui <- fluidPage(
  titlePanel("Football Manager Squad Evaluation"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput(
        "attribute",
        "Select Player Attribute:",
        choices = colnames(data_df)[3:ncol(data_df)],
        selected = "Height"
      ),
      sliderInput(
        "n",
        "Number of Top Players:",
        min = 2,
        max = 30,
        value = 10
      ),
      sliderInput(
        "textSize",
        "Label Size:",
        min = 2,
        max = 10,
        value = 4,
        step = 0.5
      ),
      checkboxInput("show_names", "Show Names", TRUE),
      checkboxInput("show_ages", "Show Ages", TRUE),
      checkboxGroupInput(
        "playerClass",
        label = "Select player classes to view",
        choices = player_class_choices,
        selected = names(player_class_choices)
      ),
      # Button for select/deselect all
      actionButton("selectAll", "Select / Deselect All")
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel("Coordinate Plot", uiOutput("dynamicCoordinatePlots"),
                 radioButtons("viewType", "Select View Type:", choices = c("2D", "3D"), selected = "2D")),
        tabPanel("Bar Graph", plotOutput("barGraph")),
        tabPanel("Histogram", plotOutput("histogramPlot")),
        tabPanel("Mean Values", 
                 #div(style = "position:relative; height:calc(100vh - 200px);",
                 div(style = "position:relative; height:calc(100vh- 150px);",
                     plotlyOutput("meanValueBarGraph", height = "800px")),
                 div(style = "position:relative; width:100%;", 
                     actionButton("toggleOrder", "Toggle Ordering", style = "width:100%;"))
        )
      )
    )
  )
)