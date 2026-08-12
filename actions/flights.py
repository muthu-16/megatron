import logging
import requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class FlightSearch:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def search_flights(self, origin: str, destination: str, date: str, language: str = 'en') -> List[Dict[str, Any]]:
        logger.info(f"Searching flights from {origin} to {destination} on {date}")
        
        if self.api_key:
            return self._search_aviationstack(origin, destination, date)
        else:
            return self._fallback_search(origin, destination, date)

    def _search_aviationstack(self, origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
        url = f"http://api.aviationstack.com/v1/flights?access_key={self.api_key}&dep_iata={origin}&arr_iata={destination}"
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return self.format_flights(data.get('data', []))
            else:
                logger.error(f"Aviationstack error: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Aviationstack request failed: {e}")
            return []

    def _fallback_search(self, origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
        logger.warning("Using fallback flight search (mock/scraping).")
        # Placeholder for web scraping fallback logic
        return []

    def format_flights(self, flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted = []
        for f in flights:
            formatted.append({
                "flight_number": f.get("flight", {}).get("iata"),
                "airline": f.get("airline", {}).get("name"),
                "departure": f.get("departure", {}).get("estimated"),
                "arrival": f.get("arrival", {}).get("estimated"),
                "status": f.get("flight_status")
            })
        return formatted
