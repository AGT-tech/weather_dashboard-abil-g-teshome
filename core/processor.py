"""Data processing """

from typing import Dict, List
import statistics


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
        """Calculate statistics from weather history with trend detection"""
        if not history:
            return {}

        temps = [h['temperature'] for h in history]
        trend = self.detect_trend(temps)

        return {
            'average': round(statistics.mean(temps), 1),
            'minimum': min(temps),
            'maximum': max(temps),
            'trend': trend
        }

    @staticmethod
    def detect_trend(temps: List[int]) -> str:
        """Detect trend in temperature using linear regression"""
        n = len(temps)
        if n < 2:
            return "stable"

        x = list(range(n))
        y = temps

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((xi - mean_x)*(yi - mean_y) for xi, yi in zip(x, y))
        denominator = sum((xi - mean_x)**2 for xi in x)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "rising"
        else:
            return "falling"

    @staticmethod
    def convert_temperature(temp, from_unit, to_unit):
        if from_unit == to_unit:
            return temp
        return (temp - 32) * 5 / 9 if to_unit == "metric" else (temp * 9 / 5) + 32
