"""
weather_api.py

This module provides a WeatherAPI class to interact with the OpenWeatherMap API.
It supports current weather and 5-day forecast retrieval, with built-in caching,
retry logic, and structured error handling.
"""

import requests
from dataclasses import dataclass, field
from typing import Optional, Dict, Tuple
import logging
import time


@dataclass
class WeatherAPI:
    """
    Class to interact with the OpenWeatherMap API.
    
    Attributes:
        api_key (str): API key for authentication.
        timeout (int): Timeout in seconds for API requests.
        base_url (str): URL for the current weather API endpoint.
        max_retries (int): Number of retry attempts for failed requests.
        cache_duration (int): Cache expiry duration in seconds.
        cache (dict): In-memory cache to store API responses.
    """
    api_key: str
    timeout: int = 10
    base_url: str = "http://api.openweathermap.org/data/2.5/weather"
    max_retries: int = 3
    cache_duration: int = 600  # seconds (10 minutes)
    cache: Dict[Tuple[str, str], Tuple[Dict, float]] = field(default_factory=dict)

    def fetch_weather(self, city: str, units: str = "imperial") -> Tuple[Optional[Dict], Optional[str]]:
        """
        Fetch current weather data for a given city with optional unit specification.

        Args:
            city (str): City name to fetch weather for.
            units (str): Measurement units ('imperial', 'metric', etc.).

        Returns:
            Tuple[Optional[Dict], Optional[str]]: Weather data and error message (if any).
        """
        cache_key = (city.lower(), units)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached, None

        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                # Make GET request to current weather endpoint
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                # Cache the response and return it
                self._set_cache_response(cache_key, data)
                return data, None

            except requests.exceptions.HTTPError as e:
                # Handle known HTTP status codes
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

            except requests.RequestException:
                logging.exception("General request error:")
                return None, "An unknown error occurred. Please try again later."

        return None, "Failed after multiple attempts."

    def fetch_forecast(self, city: str, units: str = "imperial") -> Tuple[Optional[Dict], Optional[str]]:
        """
        Fetch 5-day forecast weather data for a given city with optional unit specification.

        Args:
            city (str): City name to fetch forecast for.
            units (str): Measurement units ('imperial', 'metric', etc.).

        Returns:
            Tuple[Optional[Dict], Optional[str]]: Forecast data and error message (if any).
        """
        cache_key = (f"forecast:{city.lower()}", units)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached, None

        forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': units
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                # Make GET request to forecast endpoint
                response = requests.get(forecast_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                # Cache and return the data
                self._set_cache_response(cache_key, data)
                return data, None

            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    return None, "City not found for forecast."
                logging.error(f"Forecast HTTPError ({response.status_code}): {response.text}")
                return None, f"Forecast error: {response.status_code}"

            except requests.exceptions.Timeout:
                logging.warning(f"Forecast timeout attempt {attempt} for city '{city}'")
                if attempt == self.max_retries:
                    return None, "Forecast request timed out."

            except requests.exceptions.RequestException:
                logging.exception("Forecast request failed:")
                return None, "Forecast request failed due to an unexpected error."

        return None, "Failed to fetch forecast after retries."

    def _get_cached_response(self, key: Tuple[str, str]) -> Optional[Dict]:
        """
        Return cached data if still valid based on cache_duration.

        Args:
            key (Tuple[str, str]): Unique key representing the request (e.g., city and units).

        Returns:
            Optional[Dict]: Cached data if present and not expired, else None.
        """
        cached = self.cache.get(key)
        if cached:
            data, timestamp = cached
            if time.time() - timestamp < self.cache_duration:
                logging.info(f"Returning cached data for key: {key}")
                return data
            else:
                # Remove expired cache entry
                del self.cache[key]
        return None

    def _set_cache_response(self, key: Tuple[str, str], data: Dict) -> None:
        """
        Store response data in the cache with a timestamp.

        Args:
            key (Tuple[str, str]): Unique key for the cached data.
            data (Dict): Response data to cache.
        """
        self.cache[key] = (data, time.time())
