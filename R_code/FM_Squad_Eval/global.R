# Sample data
data_df <- data.frame(
  Name = c("Player Abacus", "Player Bolshivek", "Player Comrade", "Player Druze", "Player Erroll"),
  Best_Pos = c("GK", "D (C)", "AM (L)", "ST (C)", "M (C)"),
  Height = c(180, 185, 170, 175, 182),
  Weight = c(70, 78, 65, 72, 68),
  Age = c(24, 26, 22, 23, 25)
)

# Create LastName to create LastName label option
data_df$LastName <- sapply(strsplit(data_df$Name, " "), tail, 1)

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