# src/agents/weather_agent.py
import requests
from config.settings import WEATHER_API_KEY

OWM_BASE = "https://api.openweathermap.org/data/2.5/weather"

def fetch_weather_by_city(city: str, units: str = "metric") -> dict:
    """
    Calls OpenWeatherMap current weather API.
    Returns parsed JSON (or raises).
    """
    if not WEATHER_API_KEY:
        raise RuntimeError("WEATHER_API_KEY not set in environment")

    params = {"q": city, "appid": WEATHER_API_KEY, "units": units}
    resp = requests.get(OWM_BASE, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # Minimal normalized result
    result = {
        "city": data.get("name"),
        "description": data["weather"][0]["description"] if data.get("weather") else None,
        "temp": data["main"]["temp"] if data.get("main") else None,
        "feels_like": data["main"].get("feels_like") if data.get("main") else None,
        "humidity": data["main"].get("humidity") if data.get("main") else None,
        "raw": data,
    }
    return result

