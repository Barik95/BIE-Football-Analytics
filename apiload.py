import requests
import time
import json
import os
from login import KEY

# API details
API_KEY = KEY
BASE_URL = 'https://api.football-data.org/v4'

headers = {
    'X-Auth-Token': API_KEY
}

# Parameters and file names
competition_id = 2021
seasons = [2021, 2022, 2023]  # List of seasons to fetch data for
matchday = 38  # Example matchday

# Use the 'data' folder inside the Docker container
file_name_teams = 'data/data/competition_teams_3y.json'
file_name_standings = 'data/data/competition_standings_3y.json'
file_name_matches = 'data/data/last_season_games_3y.json'
file_name_topscorers = 'data/data/topscorers_3y.json'

# Functions
def get_data(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:  # Resource not found
        print(f"Error: The resource was not found. Please check the competition ID or endpoint. Endpoint: {endpoint}")
    elif response.status_code == 429:  # Rate limit exceeded
        retry_after = int(response.headers.get('Retry-After', 10))
        time.sleep(retry_after)
        return get_data(endpoint)
    else:
        response.raise_for_status()

def append_json(data, filename):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # If file exists, load existing data and append new data, otherwise create a new structure
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # Ensure the existing data is a list
    if not isinstance(existing_data, list):
        existing_data = [existing_data]

    # Append new data to the list
    existing_data.append(data)
    
    # Save the updated data to the JSON file
    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=4)
    
    print(f"Successfully updated {filename} with season {data['season_year']} data.")

# Fetch and save data for each season
for season_year in seasons:
    # Fetch and save teams data
    endpoint_teams = f'competitions/{competition_id}/teams?season={season_year}'
    teams_data = get_data(endpoint_teams)
    if teams_data:
        teams_data['season_year'] = season_year
        append_json(teams_data, file_name_teams)

    # Fetch and save standings data
    endpoint_standings = f'competitions/{competition_id}/standings?season={season_year}&matchday={matchday}'
    standings_data = get_data(endpoint_standings)
    if standings_data:
        standings_data['season_year'] = season_year
        append_json(standings_data, file_name_standings)

    # Fetch and save matches data
    endpoint_matches = f'competitions/{competition_id}/matches?season={season_year}'
    matches_data = get_data(endpoint_matches)
    if matches_data:
        matches_data['season_year'] = season_year
        append_json(matches_data, file_name_matches)

    # Fetch and save topscorers data
    endpoint_topscorers = f'competitions/{competition_id}/scorers?season={season_year}'
    topscorers_data = get_data(endpoint_topscorers)
    if topscorers_data:
        topscorers_data['season_year'] = season_year
        append_json(topscorers_data, file_name_topscorers)
