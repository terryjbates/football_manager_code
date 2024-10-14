Sys.setlocale("LC_CTYPE", "hr_HR.UTF-8")
options(encoding = "UTF-8")
#html_file <- "sesvete_2023_07.html"
library(tidyverse)
library(rvest)


html_file <- "2025_jul_spezia.html"

kawa_webpage <- read_html(html_file)

# Extract the table
kawa_player_table <- html_nodes(kawa_webpage, "table") %>% html_table(fill = TRUE)

# Convert the table to a data frame
kawa_player_data <- kawa_player_table[[1]]

# Change `Best Pos` to Best_Pos 
# kawa_player_data <- player_data %>% mutate(Best_Pos = `Best Pos`)
kawa_player_data$Best_Pos <- kawa_player_data$`Best Pos`

# Remove duplicate columns
kawa_player_data <- kawa_player_data[!duplicated(colnames(kawa_player_data))]


Encoding(kawa_player_data$Name) <- "UTF-8"
# Convert height into CM
# Define a function to convert height from feet and inches to centimeters
ft_to_cm <- function(ft, inch) {
  # Convert feet and inches to centimeters
  cm <- (ft * 12 + inch) * 2.54
  # Return the result
  return(cm)
}

# Split the height column into feet and inches
height_split <- strsplit(kawa_player_data[['Height']], "'")

# Extract the feet and inches values
feet <- sapply(height_split, function(x) as.numeric(x[1]))
inches <- sapply(height_split, function(x) as.numeric(gsub('"', '', x[2])))


# Convert the height to centimeters
height_cm <- ft_to_cm(feet, inches)

# Define a function to convert from centimeters to fractional Imperial
cm_to_ft <- function(cm) {
  # Convert feet and inches to centimeters
  ft <-  round((cm / 30.48), 2)
  # Return the result
  return(ft)
}

# Overwrite the Height data
kawa_player_data[['Height']] <- cm_to_ft(height_cm) 

# Save data for later
write.table(kawa_player_data, file='kawa_player_data.txt', sep= "\t", row.names=FALSE)

# To import data (in global.R)
df_data <- read.table("kawa_player_data.txt", header=TRUE, sep="\t")


