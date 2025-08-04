"""Data processing module for weather data conversion and analysis."""

from typing import Dict
import logging


class DataProcessor:
    """
    A class to process and analyze weather data obtained from external APIs.
    
    This class provides methods to:
    - Convert raw weather API responses into a simplified, structured dictionary
      tailored for internal use or UI display.
    - Convert temperatures between Fahrenheit and Celsius scales.

    Attributes:
        logger (logging.Logger): Logger instance for error and debug messages.
    """

    def __init__(self):
        # Set up a logger for this class
        self.logger = logging.getLogger(__name__)

    def process_api_response(self, data: Dict, units: str = "imperial") -> Dict:
        """
        Convert raw API weather response into a structured internal format 
        including temperature, humidity, description, and wind speed with units.

        Args:
            data (Dict): The raw JSON/dict response from the weather API.
            units (str, optional): Unit system for temperature and wind speed.
                Accepts 'imperial' for Fahrenheit/mph or 'metric' for Celsius/m/s.
                Defaults to "imperial".

        Returns:
            Dict: A dictionary containing processed weather details:
                - city (str): Name of the city/location.
                - temperature (int): Rounded current temperature.
                - feels_like (int): Rounded 'feels like' temperature.
                - humidity (int): Humidity percentage.
                - description (str): Weather condition description.
                - wind_speed (str): Wind speed with appropriate unit.
                - unit (str): Temperature unit symbol ("°F" or "°C").
        """
        if not data:
            # Return an empty dict if no data was provided
            return {}

        try:
            # Determine unit symbols based on the selected units (imperial or metric)
            unit_symbol = "°F" if units == "imperial" else "°C"
            wind_unit = "mph" if units == "imperial" else "m/s"

            # Extract and format the relevant weather data
            return {
                'city': data.get('name', 'Unknown'),  # Default to 'Unknown' if name is missing
                'temperature': round(data.get('main', {}).get('temp', 0)),  # Round temperature
                'feels_like': round(data.get('main', {}).get('feels_like', 0)),  # Round 'feels like' temp
                'humidity': data.get('main', {}).get('humidity', 0),  # Default to 0% if missing
                'description': data.get('weather', [{}])[0].get('description', ''),  # Weather summary
                'wind_speed': f"{data.get('wind', {}).get('speed', 0)} {wind_unit}",  # Wind speed + unit
                "unit": unit_symbol  # Unit symbol to display next to temperature
            }

        except (KeyError, IndexError, TypeError) as e:
            # Log and return empty dict on error while parsing the data
            self.logger.exception("Error processing weather API data")
            return {}

    @staticmethod
    def convert_temperature(temp: float, from_unit: str, to_unit: str) -> float:
        """
        Convert temperature value between Fahrenheit and Celsius units.

        Args:
            temp (float): Temperature value to convert.
            from_unit (str): Current unit of the temperature ("imperial" or "metric").
            to_unit (str): Desired unit to convert to ("imperial" or "metric").

        Returns:
            float: Converted temperature value.
        """
        if from_unit == to_unit:
            # No conversion needed if units match
            return temp

        # Convert Fahrenheit to Celsius if target is metric
        if to_unit == "metric":
            return (temp - 32) * 5 / 9

        # Otherwise, convert Celsius to Fahrenheit
        return (temp * 9 / 5) + 32
