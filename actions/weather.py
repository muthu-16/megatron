import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def _read_config_key(key: str, default: str = "") -> str:
    """Read a value from config.yaml safely."""
    try:
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from config.secrets import get_secret
        return get_secret(key, default) or default
    except Exception:
        return default

class WeatherService:
    def __init__(self, api_key: Optional[str] = None, units: str = 'metric'):
        self.api_key = api_key or _read_config_key("openweathermap_api_key", "")
        self.units = units or _read_config_key("weather_units", "metric")

    def get_weather(self, location: str, language: str = 'en') -> Optional[Dict[str, Any]]:
        logger.info(f"Getting weather for {location} in {language}")
        if not self.api_key:
            logger.error("Weather API key not set.")
            return None
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.api_key}&units={self.units}&lang={language}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self.format_weather(data)
            else:
                logger.error(f"Weather API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
            return None

    def format_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return {
                "location": data.get("name", "Unknown"),
                "description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"]
            }
        except KeyError as e:
            logger.error(f"Error formatting weather data: {e}")
            return data
