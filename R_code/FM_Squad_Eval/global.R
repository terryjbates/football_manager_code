# Read in tactical style data
source("./tactical_style_data.R")

# Read in tactical styles
#tactical_styles <- read_tactical_styles("./tactical_style_weightings.csv")

# "Real" FM data read from disk. See bottom for previous data_df.

data_df <-
  read.table("kawa_player_data.txt", header = TRUE, sep = "\t")

# Create LastName to create LastName label option
data_df$LastName <- sapply(strsplit(data_df$Name, " "), tail, 1)


# Try to sort attributes lexicographically
data_df_colnames <- colnames(data_df)
data_df_colnames <- sort(data_df_colnames)

# Create new data frame, same size as data_df
new_df <- data.frame(matrix(ncol = ncol(data_df), nrow = nrow(data_df)))

# We use the sorted column names
colnames(new_df) <- data_df_colnames

# Copy the data from original unsorted data_df into new_df
for (col in names(data_df)) {
  new_df[[col]] <- data_df[[col]]
}

# Set data_df to be new_df
data_df <- new_df

# Goalkeeper attribs for removal

gk_attribs <- c("Kic","Ref", "Han", "Aer", "Com","Cmd", "1v1", "Thr", "Agi", "Ecc",
                "Pun", "Tro","X1v1", "TRO" )
#gk_attribs <- c('Kic', 'Pun')


#Defenders <- c("Hea", "Mar", "Tck", "Pos", "Jmp", "Str")

class_attrib_lookup <- list(Defenders = c("Hea", "Mar", "Tck", "Pos", "Jum", "Str"),
                            Goalkeepers = c("Kic","Ref", "Han", "Aer", "Com","Cmd", 
                                            "1v1", "Thr", "Agi", "Ecc", "Pun", 
                                            "Tro","X1v1", "TRO" ),
                            "Central Midfielders" = c("Pas", "Tck", "OtB", "Tea",
                                                      "Wor", "Sta"),
                            "Defensive Midfielders"= c("Tck","Ant", "Cnt", "Pos",
                                                       "Tea","Fir","Tec","Cmp",
                                                       "Vis", "Pas"),
                            "Central Midfielders" = c("Fir", "Pas", "Tck", "Dec",
                                                      "Tea"),
                            "Attacking Midfielders" = c("Fir", "Pas", "Dec", "Tec",
                                                        "Cmp", "Dec", "OtB", "Tea",
                                                        "Vis","Fla"),
                            Forwards = c("Dri", "Fin", "Fir", "Tec", "Cmp",
                                         "OtB", "Cmp", "Acc", "Pac", "Str")
                            )

# Position mapping
position_mapping_default <- list(
  `0,0` = c("GK"),
  `-2,1` = c("D (L)", "D/WB (L)"),
  `-1,1` = c("D (C)"),
  `0,1` = c("D (C)"),
  `1,1` = c("D (C)"),
  `2,1` = c("D (R)", "D/WB (R)"),
  `-2,2` = c("D/WB (L)"),
  `-1,2` = c("DM"),
  `0,2` = c("DM"),
  `1,2` = c("DM"),
  `2,2` = c("D/WB (R)"),
  `-2,3` = c("M/AM (L)"),
  `-1,3` = c("M (C)"),
  `0,3` = c("M (C)"),
  `1,3` = c("M (C)"),
  `2,3` = c("M/AM (R)"),
  `-2,4` = c("M/AM (L)", "AM (L)"),
  `-1,4` = c("AM (C)"),
  `0,4` = c("AM (C)"),
  `1,4` = c("AM (C)"),
  `2,4` = c("M/AM (R)", "AM (R)"),
  `-1,5` = c("ST (L)"),
  `0,5` = c("ST (C)"),
  `1,5` = c("ST (R)")
)

# Player class mapping
player_class <- list(
  `0` = c("Goalkeepers"),
  `1` = c("Defenders"),
  `2` = c("Defensive Midfielders"),
  `3` = c("Central Midfielders"),
  `4` = c("Attacking Midfielders"),
  `5` = c("Forwards")
)


# Store the choices for player classes statically to ensure consistency
player_class_choices <- c(
  "Goalkeepers" = "0",
  "Defenders" = "1",
  "Defensive Midfielders" = "2",
  "Central Midfielders" = "3",
  "Attacking Midfielders" = "4",
  "Forwards" = "5"
)

# Sample data
#data_df <- data.frame(
#  Name = c("Player Abacus", "Player Bolshivek", "Player Comrade", "Player Druze", "Player Erroll"),
#  Best_Pos = c("GK", "D (C)", "AM (L)", "ST (C)", "M (C)"),
#  Height = c(180, 185, 170, 175, 182),
#  Weight = c(70, 78, 65, 72, 68),
#  Age = c(24, 26, 22, 23, 25)
#)

# Sample data with clubs
#data_df <- data.frame(
#  Name = c("Player Abacus", "Player Bolshivek", "Player Comrade", "Player Druze", "Player Erroll"),
#  Best_Pos = c("GK", "D (C)", "AM (L)", "ST (C)", "M (C)"),
#  Height = c(180, 185, 170, 175, 182),
#  Weight = c(70, 78, 65, 72, 68),
#  Age = c(24, 26, 22, 23, 25),
#  Club = c("Kashima", "Kashima", "Kawasaki", "VentForet", "Kawasaki")
#)

# Sample data_df
#  data_df <- data.frame(
#    Name = c("Player Abacus", "Player Bolshivek", "Player Comrade", "Player Druze"),
#    Best_Pos = c("M/AM (L)", "ST (C)", ""M/AM (R)", "M (C)"),
#    Height = c(180, 190, 175, 185),
#    Morale = c(80, 90, 75, 85),
#    ACC = c(90, 85, 88, 78),
#    stringsAsFactors = FALSE
#  )
# Sample data
#  data_df <- data.frame(
#    Name = c("Player A", "Player B", "Player C", "Player D", "Player E"),
#    Best_Pos = c("GK", "CB", "RW", "ST", "CM"),
#    Height = c(180, 185, 170, 175, 182),
#    Weight = c(70, 78, 65, 72, 68),
#    Age = c(24, 26, 22, 23, 25)
#  )


#  data_df <- data.frame(
#    Name = c("Player Abacus", "Player Bolshivek", "Player Comrade", "Player Druze", "Player Erroll"),
#    Best_Pos = c("GK", "CB", "RW", "ST", "CM"),
#    Height = c(180, 185, 170, 175, 182),
#    Weight = c(70, 78, 65, 72, 68),
#    Age = c(24, 26, 22, 23, 25)
#  ) 