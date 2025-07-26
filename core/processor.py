"""Data processing"""

from typing import Dict
import logging


class DataProcessor:
    """Processes and analyzes weather data"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_api_response(self, data: Dict, units: str = "imperial") -> Dict:
        """
        Convert raw API weather response into a structured internal format.
        """
        if not data:
            return {}

        try:
            unit_symbol = "°F" if units == "imperial" else "°C"
            wind_unit = "mph" if units == "imperial" else "m/s"

            return {
                'city': data.get('name', 'Unknown'),
                'temperature': round(data.get('main', {}).get('temp', 0)),
                'feels_like': round(data.get('main', {}).get('feels_like', 0)),
                'humidity': data.get('main', {}).get('humidity', 0),
                'description': data.get('weather', [{}])[0].get('description', ''),
                'wind_speed': f"{data.get('wind', {}).get('speed', 0)} {wind_unit}",
                "unit": unit_symbol
            }

        except (KeyError, IndexError, TypeError) as e:
            self.logger.exception("Error processing weather API data")
            return {}

    @staticmethod
    def convert_temperature(temp: float, from_unit: str, to_unit: str) -> float:
        """
        Convert temperature between Fahrenheit and Celsius.
        """
        if from_unit == to_unit:
            return temp
        return (temp - 32) * 5 / 9 if to_unit == "metric" else (temp * 9 / 5) + 32
