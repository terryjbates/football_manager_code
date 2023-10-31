library(shiny)
library(ggplot2)
library(plotly)

# Some example data
squad_data <- data.frame(
  Name = c(
    "Player Abacus",
    "Player Bolshivek",
    "Player Comrade",
    "Player Druze",
    "Player Erroll"
  ),
  Best_Pos = c("GK", "CB", "RW", "ST", "CM"),
  Height = c(180, 185, 170, 175, 182),
  Weight = c(70, 78, 65, 72, 68),
  Age = c(24, 26, 22, 23, 25)
)

# UI definition
ui <- fluidPage(
  radioButtons("viewType", "Select View Type:", choices = c("2D", "3D"), selected = "2D"),
  plotlyOutput("plot")
)

# Define server logic
server <- function(input, output) {
  output$plot <- renderPlotly({
    # 2D plot
    if (input$viewType == "2D") {
      ggplot(squad_data, aes(x = Name, y = Height)) + geom_col() + coord_flip()
      
    } else {
      # 3D plot
      plot_ly(data = squad_data, type = "scatter3d", mode = 'markers+text') %>%
        add_trace(
          x = ~ Name,
          y = ~ Weight,
          z = ~ Height,
          #text = ~ Name,
          text = ~ paste(Name,
                                      "<br>Weight: ", Weight,
                                      "<br>Height: ",Height),
          hoverinfo = "text",
          textposition = "top center",
          marker = list(size = 10) # Adjust size as needed
        ) %>%
        layout(
          scene = list(
            xaxis = list(
              title = "Players",
              linecolor = "black",
              linewidth = 2
            ),
            yaxis = list(
              title = "Weight",
              linecolor = "black",
              linewidth = 2
            ),
            zaxis = list(
              title = "Height",
              linecolor = "black",
              linewidth = 2
            )
          )
        )
    }
  })
}

shinyApp(ui = ui, server = server)
