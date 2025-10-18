import requests
from flask import current_app

BASE_URL = "https://api.rawg.io/api"

def fetch_upcoming_games(page_size=5):
    """
    Fetch upcoming games using the RAWG API.
    """
    api_key = current_app.config['RAWG_API_KEY']
    url = f"{BASE_URL}/games?key={api_key}&dates=2025-01-01,2025-12-31&ordering=released&page_size={page_size}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['results']

def fetch_game_details(game_id):
    """
    Fetch detailed information for a single game.
    """
    api_key = current_app.config['RAWG_API_KEY']
    url = f"{BASE_URL}/games/{game_id}?key={api_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def search_games(query, page_size=10):
    """
    Search for games by name.
    """
    api_key = current_app.config['RAWG_API_KEY']
    url = f"{BASE_URL}/games?key={api_key}&search={query}&page_size={page_size}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['results']
