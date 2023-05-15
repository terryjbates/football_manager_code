from bs4 import BeautifulSoup
import pandas as pd
import re

# Read the HTML file
with open('./file.html', 'r') as file:
    html_str = file.read()

# Parse the HTML string with BeautifulSoup
soup = BeautifulSoup(html_str, 'html.parser')

# Find the table in the HTML
table = soup.find('table')

# Convert the table into a DataFrame
df = pd.read_html(str(table), header=0)[0]

# Generate the prompts
for index, row in df.iterrows():
    print(f"Footballer, headshot image facing directly into camera, top of the head to 2 inches below the chin, shot with Canon EOS R3, {row['Age']} years old, {row['Height']} tall, weighing {row['Weight']}, born in {row['NoB']}, of {row['Birth Region']} descent, a {row['Personality']} personality, {row['Media Description']}, handles the press with a {row['Media Handling']} style.")
