from dataclasses import dataclass
from typing import Optional, Dict
import requests  

# Use @dataclass to automatically generate __init__, __repr__, etc.
@dataclass
class WeatherAPI:
    api_key: str                            # OpenWeatherMap API key
    timeout: int = 10                       # Request timeout in seconds (default is 10)
    base_url: str = "http://api.openweathermap.org/data/2.5/weather"  # Weather API endpoint

    def fetch_weather(self, city: str, units: str = "imperial") -> Optional[Dict]:
        """
        Fetch current weather data for a given city using OpenWeatherMap API.

        Args:
            city (str): Name of the city (e.g., "London", "New York").
            units (str): Unit system ('imperial' for Fahrenheit, 'metric' for Celsius).

        Returns:
            Optional[Dict]: Parsed JSON response as a dictionary if successful, else None.
        """
        try:
            # Send GET request with city, API key, units, and timeout
            response = requests.get(
                self.base_url,
                params={
                    'q': city,
                    'appid': self.api_key,
                    'units': units     # Use 'imperial' for °F, 'metric' for °C
                },
                timeout=self.timeout
            )
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()       # Convert response to Python dict
        except requests.RequestException as e:
            # Log any request or connection errors
            print(f"WeatherAPI Error: {e}")
            return None  # Return None on failure to indicate error
