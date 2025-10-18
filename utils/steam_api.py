import requests
from flask import current_app

BASE_URL = "https://store.steampowered.com/api"

def get_steam_game_details(appid):
    """
    Fetch detailed information for a single Steam game.
    Returns a dict with safe keys for template.
    """
    url = f"https://store.steampowered.com/api/appdetails"
    params = {
        "appids": appid,
        "cc": "us",
        "l": "en"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if not data[str(appid)]["success"]:
        return None

    game_data = data[str(appid)]["data"]

    # Preprocess fields safely
    image_url = game_data.get("header_image")
    description = game_data.get("short_description", "")
    name = game_data.get("name", "Unknown Game")
    release_date = game_data.get("release_date", {}).get("date", "Unknown")

    return {
        "name": name,
        "description": description,
        "original_release_date": release_date,
        "image_url": image_url
    }

def get_featured_games():
    """
    Fetch featured games from Steam store.
    Returns list of dicts with keys: appid, name, image_url, discounted
    """
    url = "https://store.steampowered.com/api/featuredcategories"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    games = []

    # Specials (on-sale) games
    for item in data.get("specials", {}).get("items", []):
        appid = item.get("id")
        games.append({
            "appid": appid,
            "name": item.get("name"),
            "image_url": f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
            "discounted": item.get("discount_percent", 0) > 0
        })

    # New releases
    for item in data.get("new_releases", {}).get("items", []):
        appid = item.get("id")
        games.append({
            "appid": appid,
            "name": item.get("name"),
            "image_url": f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg",
            "discounted": False
        })

    return games



