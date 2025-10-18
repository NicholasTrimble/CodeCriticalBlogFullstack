import requests
from flask import current_app
from datetime import datetime

BASE_URL = "https://www.giantbomb.com/api"

HEADERS = {
    "User-Agent": "CodeCriticalBlog/1.0",
    "Accept": "application/json"
}

def fetch_upcoming_games(limit=5):
    """
    Fetch upcoming games from Giant Bomb API.
    """
    api_key = current_app.config['GIANTBOMB_API_KEY']
    url = f"{BASE_URL}/games/"
    params = {
        "api_key": api_key,
        "format": "json",
        "sort": "original_release_date:asc",
        "filter": "original_release_date:2025-01-01|2025-12-31",
        "field_list": "id,name,original_release_date,image",
        "limit": limit
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()["results"]

def fetch_game_details(game_id):
    """
    Fetch a single game by ID.
    """
    api_key = current_app.config['GIANTBOMB_API_KEY']
    url = f"{BASE_URL}/game/{game_id}/"
    params = {
        "api_key": api_key,
        "format": "json",
        "field_list": "id,name,description,original_release_date,image,platforms,genres"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()["results"]

def search_games(query, limit=10):
    """
    Search games by name.
    """
    api_key = current_app.config['GIANTBOMB_API_KEY']
    url = f"{BASE_URL}/games/"
    params = {
        "api_key": api_key,
        "format": "json",
        "filter": f"name:{query}",
        "field_list": "id,name,original_release_date,image",
        "limit": limit
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()["results"]
