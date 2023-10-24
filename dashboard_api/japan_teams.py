import http.client
import json
from typing import Dict
from dotenv import load_dotenv
import os


load_dotenv()

# Globals
J_LEAGUE_1 = '98'
J_LEAGUE_2 = '99'
J_LEAGUE_3 = '100'
JFL = '497'
SEASON = '2023'
api_key = os.getenv('x-rapidapi-key')

if api_key is None:
    raise ValueError("API key (x-rapidapi-key) not found in environment variables.")

# Function to recursively call paginated API
def call_api(endpoint: str, params: Dict) -> dict:
    # TODO: Implement the logic for making API calls
    pass


# Save JSON data to a file
def save_json_to_disk(json_data: dict, json_out_filename: str) -> None:
    with open(json_out_filename, "w") as write_file:
        json.dump(json_data, write_file, indent=2)


def main() -> None:
    conn = http.client.HTTPSConnection("v3.football.api-sports.io")

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': api_key
    }

    conn.request("GET", f"/teams?league={J_LEAGUE_1}&season={SEASON}", headers=headers)
    res = conn.getresponse()

    # Attempt deserialization of JSON data
    json_league_data = json.load(res)
    print(json.dumps(json_league_data, indent=2))  # Print JSON data for debugging
    save_json_to_disk(json_league_data, 'jleague_data.json')


if __name__ == "__main__":
    main()
