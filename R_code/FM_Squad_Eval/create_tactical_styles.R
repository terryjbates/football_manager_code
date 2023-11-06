library(tibble)
library(readr)
library(data.table)

# Comprehensive tactical styles data frame with distinct weightings and additional attributes
tactical_styles_df <- tribble(
  ~Style,                  ~Det, ~Pac, ~Acc, ~Ant, ~Agg, ~Bra, ~Dec, ~Pos, ~Jum, ~Nat, ~Fir, ~Pas, ~Fla, ~Cmp, ~Vis, ~Tea, ~Dri, ~Wor, ~OtB, ~Cro, ~Tck, ~Formations,
  "Gegenpress",            18,   14,   14,   16,   12,   8,    10,   6,    3,    2,    4,    5,    4,    6,    7,    5,    9,    11,   10,   9,    8,    "4-2-3-1, 3-4-3, 3-1-4-2",
  "Tiki-Taka",             8,    12,   12,   20,   6,    10,   18,   15,   1,    1,    12,   18,   15,   10,   17,   16,   5,    13,   9,    10,   5,    "4-3-3 False 9, 3-4-3 Diamond, 3-6-1",
  "Route One",             5,    18,   5,    7,    15,   16,   4,    6,    20,   10,   2,    2,    1,    2,    3,    1,    4,    5,    3,    3,    16,   "4-4-2, 5-3-2, 4-1-3-2",
  "Counter-Attack",        6,    16,   14,   10,   8,    7,    6,    8,    12,   1,    5,    13,   7,    6,    8,    7,    9,    10,   7,    14,   12,   "4-4-2 Classic, 4-1-4-1, 5-4-1",
  "Possession",            10,   6,    10,   17,   5,    20,   19,   14,   2,    3,    9,    11,   16,   17,   19,   11,   12,   14,   13,   12,   4,    "4-3-3 Holding, 4-5-1, 4-1-4-1",
  "Direct Play",           12,   8,    8,    9,    18,   6,    5,    4,    17,   15,   3,    4,    6,    5,    4,    3,   13,   12,   11,   11,   14,   "4-2-3-1 Wide, 3-4-1-2, 4-3-1-2",
  "Fluid Counter-Attack",  7,    17,   16,   13,   7,    9,    5,    7,    11,   4,    6,    15,   13,   10,   9,    8,   10,   15,   12,   13,   11,   "4-3-3, 3-5-2, 5-2-2-1",
  "Control Possession",    9,    7,    13,   19,   4,    18,   19,   13,   2,    3,   11,   17,   19,   14,   17,   13,    6,   16,   15,   15,   3,    "4-1-4-1 DM Wide, 4-2-3-1 Deep, 3-4-3",
  "Pressing",              17,   11,   9,    13,   14,   11,   9,    7,    6,    3,   10,   12,   11,   13,   15,   12,   14,   16,   13,   8,    7,    "4-1-4-1 DM Wide, 4-2-3-1 Deep, 3-4-3",
  "Total Football",        11,   13,   13,   15,   9,    12,   14,   11,   2,    2,   14,   16,   15,   13,   14,   16,   15,   18,   17,   6,    10,   "3-4-3 Diamond, 4-3-3, 4-2-3-1",
  "Vertical Tiki Taka",    9,    10,   15,   18,   7,    13,   17,   10,   1,    1,   16,   17,   16,   12,   18,   15,   6,    14,   11,   2,    5,    "4-3-3 Holding, 3-2-2-3, 3-1-4-2"
)


# Delete an unwanted row by index "Total Football"
#tactical_styles_df <- tactical_styles_df[-11, ]

# Write the data frame to a CSV file
write_csv(tactical_styles_df, "C:/Users/lover/Documents/Github/football_manager_code/R_code/FM_Squad_Eval/tactical_style_weightings.csv")


# # Comprehensive tactical styles data frame with distinct weightings and additional attributes
# tactical_styles_df <- tribble(
#   ~Style,                  ~Det, ~Pac, ~Acc, ~Ant, ~Agg, ~Bra, ~Dec, ~Pos, ~Jum, ~Nat, ~Fir, ~Pas, ~Fla, ~Cmp, ~Vis, ~Tea, ~Dri, ~Wor, ~OtB, ~Formations,
#   "Gegenpress",            20,   17,   17,   15,   13,   10,    8,    5,    3,    2,    5,    6,    4,    5,    7,    6,    8,    12,   9,    "4-3-3,3-4-3,3-5-2",
#   "Tiki-Taka",             10,   15,   15,   18,    8,   12,   20,   10,    1,    1,   15,   20,   10,   12,   18,   15,   7,    14,   11,   "4-3-3 Hold,2-3-2-3,3-1-4-2",
#   "Route One",             10,   20,   10,    8,   12,   15,    5,    7,   15,    8,    2,    3,    2,    3,    4,    3,    5,    7,    6,    "4-4-2,5-3-2,4-2-4",
#   "Counter-Attack",         8,   18,   15,   12,   10,   10,    7,    9,   10,    1,    7,   14,    6,    7,    9,    8,   10,   11,    8,    "4-4-2 Classic,4-2-3-1,5-4-1",
#   "Possession",            12,    8,   12,   15,    7,   18,   20,   13,    2,    3,   10,   12,   15,   18,   20,   12,   13,   15,   14,   "4-3-3 DM Wide,4-5-1,4-1-4-1",
#   "Direct Play",           15,   10,   10,   10,   15,    8,    7,    5,   18,   12,    4,    5,    7,    6,    5,    4,   14,   13,   12,   "4-2-3-1 Wide,3-4-1-2,4-3-1-2",
#   "Fluid Counter-Attack",   7,   18,   17,   14,    9,   11,    6,    8,   10,    5,    8,   16,   14,   11,   10,    9,   11,   16,   13,   "4-3-3,3-5-2,5-2-3",
#   "Control Possession",    10,   10,   14,   18,    8,   20,   20,   12,    2,    3,   12,   18,   20,   15,   18,   14,   15,   18,   16,   "4-5-1,4-1-4-1,3-6-1",
#   "Wing Play",              8,   12,   12,   10,   14,    9,    8,   10,   15,    2,    6,   11,   13,   12,    8,    7,   13,   10,    7,    "3-4-3,5-2-3,4-3-3 Attack",
#   "Pressing",              18,   12,   10,   14,   16,   12,   10,    8,    7,    3,   11,   13,   12,   14,   16,   13,   15,   17,   14,   "4-1-4-1 DM Wide,4-2-3-1 Deep,3-3-1-3",
#   "Total Football",        12,   14,   14,   16,   10,   13,   15,   12,    2,    2,   13,   17,   16,   14,   15,   17,   16,   19,   18,   "3-4-3 Diamond,3-4-3 Flat,4-3-3",
#   "Vertical Tiki Taka",    11,   13,   16,   20,    9,   14,   18,   11,    1,    1,   18,   19,   17,   13,   19,   16,    8,   15,   12,   "4-3-3 Hold,3-2-4-1,3-3-3-1"
# )
