import requests
from dataclasses import dataclass
from typing import Optional, Dict, Tuple
import logging


@dataclass
class WeatherAPI:
    api_key: str
    timeout: int = 10
    base_url: str = "http://api.openweathermap.org/data/2.5/weather"
    max_retries: int = 3

    def fetch_weather(self, city: str, units: str = "imperial") -> Tuple[Optional[Dict], Optional[str]]:
        """
        Fetch current weather data from the OpenWeatherMap API.

        Returns:
            Tuple[Optional[Dict], Optional[str]]: (weather_data, error_message)
        """
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json(), None

            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    return None, "Invalid API key. Check your credentials."
                elif response.status_code == 404:
                    return None, "City not found. Please check the city name."
                elif response.status_code == 429:
                    return None, "API rate limit exceeded. Please wait and try again."
                else:
                    logging.error(f"HTTPError ({response.status_code}): {response.text}")
                    return None, f"Unexpected error: {response.status_code}"

            except requests.exceptions.Timeout:
                logging.warning(f"Timeout attempt {attempt} for city '{city}'")
                if attempt == self.max_retries:
                    return None, "Request timed out. Please check your connection."

            except requests.exceptions.ConnectionError:
                logging.error("Connection error occurred.")
                return None, "Network connection error. Please try again."

            except requests.RequestException as e:
                logging.exception("General request error:")
                return None, "An unknown error occurred. Please try again later."

        return None, "Failed after multiple attempts."
