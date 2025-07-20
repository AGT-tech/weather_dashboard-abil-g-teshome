# core/processor.py
"""Data processing module"""

from typing import Dict, List
import statistics
from scipy.stats import linregress

class DataProcessor:
    """Processes and analyzes weather data"""

    def process_api_response(self, data: Dict, units="imperial") -> Dict:
        """Convert API response to internal format"""
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
            print(f"Error processing data: {e}")
            return {}

    def calculate_statistics(self, history: List[Dict]) -> Dict:
        """Calculate statistics from weather history"""
        if not history:
            return {}

        temps = [h['temperature'] for h in history]

        # Calculate linear regression slope to detect trend
        x_vals = list(range(len(temps)))
        if len(temps) > 1:
            regression = linregress(x_vals, temps)
            slope = regression.slope
        else:
            slope = 0

        # Determine trend based on slope threshold
        threshold = 0.1  # You can adjust sensitivity here
        if slope > threshold:
            trend = "rising"
        elif slope < -threshold:
            trend = "falling"
        else:
            trend = "stable"

        return {
            'average': round(statistics.mean(temps), 1),
            'minimum': min(temps),
            'maximum': max(temps),
            'slope': slope,
            'trend': trend
        }

    @staticmethod
    def convert_temperature(temp, from_unit, to_unit):
        if from_unit == to_unit:
            return temp
        return (temp - 32) * 5 / 9 if to_unit == "metric" else (temp * 9 / 5) + 32

    def export_to_csv(self, history, file_path=""):
        import csv

        if not history:
            return

        keys = history[0].keys()
        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(history)
