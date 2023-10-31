# Read in data
kawa_data <-read.table("kawa_player_data.txt", header=TRUE, sep="\t")

# Extract last names
last_names <-
  sapply(strsplit(kawa_data$Name, " "), function(x)
    tail(x, 1))

# Attach last names to players
kawa_data$last_names <-last_names

# Show a plot of Cmp versus Fla
ggplot(data=kawa_data, aes(x=Fla,y=Cmp)) +
  geom_point(aes(color=Position), show.legend=FALSE) + # Omit the legend
  facet_wrap(~Position) +  # Create multiple graphs by position
  geom_text(aes(label=last_names)) # Add a label of last name to ID player




