library(shiny)
library(profvis)

# Load the UI and Server definitions

source("ui.R")
source("server.R")

# Profile the app

profvis({
  library(shiny)
  shinyApp(ui, server)
  
})
