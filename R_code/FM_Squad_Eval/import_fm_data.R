html_file <- "test_player_shiny.html"
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

# Save data for later
write.table(kawa_player_data, file='kawa_player_data.txt', sep= "\t", 
            row.names=FALSE)

# To import data (in global.R)
 df_data <- read.table("kawa_player_data.txt", header=TRUE, sep="\t")
 