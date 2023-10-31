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

# Use diamonds data set, use fill = cut
ggplot(data=diamonds) +
  geom_bar(mapping = aes(x=color, fill=cut)) +
  facet_wrap(~cut)

# Facet grid for two variables
# Vertically for 1st variable
# Horizontally for 2nd variable

ggplot(data = penguins) + 
  geom_point(mapping=aes(x = flipper_length_mm, y = body_mass_g, color=species)) +
  facet_grid(sex~species)  


ggplot(data = penguins) + 
  geom_point(mapping=aes(x = flipper_length_mm, y = body_mass_g, color=species)) +
  facet_grid(~species)  

ggplot(data = penguins) + 
  geom_point(mapping=aes(x = flipper_length_mm, y = body_mass_g, color=species)) +
  facet_grid(~sex)  
