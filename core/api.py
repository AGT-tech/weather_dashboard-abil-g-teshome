import requests
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple
import logging
import time


@dataclass
class WeatherAPI:
    api_key: str
    timeout: int = 10
    base_url: str = "http://api.openweathermap.org/data/2.5/weather"
    max_retries: int = 3
    cache_duration: int = 600  # Cache validity in seconds (10 minutes)
    cache: Dict[Tuple[str, str], Tuple[Dict, float]] = field(default_factory=dict)

    def fetch_weather(self, city: str, units: str = "imperial") -> Tuple[Optional[Dict], Optional[str]]:
        """
        Fetch current weather data from the OpenWeatherMap API with caching.

        Returns:
            Tuple[Optional[Dict], Optional[str]]: (weather_data, error_message)
        """
        cache_key = (city.lower(), units)
        current_time = time.time()

        # Return cached response if valid
        if cache_key in self.cache:
            cached_response, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_duration:
                logging.info(f"Returning cached weather data for '{city}'")
                return cached_response, None
            else:
                # Cache expired
                del self.cache[cache_key]

        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                # Cache the successful response
                self.cache[cache_key] = (data, current_time)
                return data, None

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
