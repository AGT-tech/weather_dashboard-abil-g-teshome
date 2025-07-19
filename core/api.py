from dataclasses import dataclass
from typing import Optional, Dict
import requests  

# Use @dataclass to automatically generate __init__, __repr__, etc.
@dataclass
class WeatherAPI:
    api_key: str                            # OpenWeatherMap API key
    timeout: int = 10                       # Optional request timeout (default 10s)
    base_url: str = "http://api.openweathermap.org/data/2.5/weather"  # API endpoint

    # Fetch weather data for a given city
    def fetch_weather(self, city: str, units: str = "imperial") -> Optional[Dict]:
        try:
            # Build and send GET request with query parameters
            response = requests.get(
                self.base_url,
                params={
                    'q': city,
                    'appid': self.api_key,
                    'units': units     # Fahrenheit; use 'metric' for Celsius
                },
                timeout=self.timeout
            )
            response.raise_for_status()  # Raises error for 4xx/5xx responses
            return response.json()       # Return JSON response as a dictionary
        except requests.RequestException as e:
            # Log any request errors
            print(f"WeatherAPI Error: {e}")
            return None                  # Gracefully handle error with None


