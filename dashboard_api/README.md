# Intro
This folder will contain some random scripts I have been using to extract data 
from the www.api-football.com API. This can provide logos, stats, player, team,
 league info. Very Beefy!

## japan_teams.py

This is a basic script that will use the API to download all the teams in a 
specified league. We are smart, so we don't include the API key in code, using
 `dotenv` to avoid this. One must make a `.env` file and specify key-value 
 pairs:
```
x-rapidapi-host=v3.football.api-sports.io
x-rapidapi-key=<your_secret_id>
J_LEAGUE_1=98
J_LEAGUE_2=99
J_LEAGUE_3=100
JFL=497
SEASON=2023
KAWASAKI_SQUAD_ID=294
```

With this script, we can download the league data to store locally or use the 
dict, with modification, after call is finished. As-is, this downloads the
data into `jleague_data.json`

You will find entries in the JSON as so:
```
 {
      "team": {
        "id": 311,
        "name": "Albirex Niigata",
        "code": "ALB",
        "country": "Japan",
        "founded": 1955,
        "national": false,
        "logo": "https://media-4.api-sports.io/football/teams/311.png"
      },
      "venue": {
        "id": 952,
        "name": "Denka Big Swan Stadium",
        "address": "Gorou Kiyoshi 67, Chuo-ku",
        "city": "Niigata",
        "capacity": 41684,
        "surface": "grass",
        "image": "https://media-4.api-sports.io/football/venues/952.png"
      }
}
```
The image URLs are served up via CDN, so one can download logos, stadium, and 
player images at will. We can then use the team ID to drill down into squad data.