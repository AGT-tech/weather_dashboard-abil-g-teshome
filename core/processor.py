"""Data processing"""

from typing import Dict, List
import statistics


class DataProcessor:
    """Processes and analyzes weather data"""

    def process_api_response(self, data: Dict, units="imperial") -> Dict:
        """
        Convert raw API weather response into a structured internal format.
        
        Args:
            data (Dict): Raw weather data from an external API.
            units (str): Unit system to use ('imperial' or 'metric').

        Returns:
            Dict: Processed weather data including city, temperature, and other details.
        """
        if not data:
            return {}

        try:
            # Set unit symbols based on chosen unit system
            unit_symbol = "°F" if units == "imperial" else "°C"
            wind_unit = "mph" if units == "imperial" else "m/s"

            # Extract and format relevant fields from API response
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
            # Handle unexpected or missing data formats gracefully
            print(f"Error processing data: {e}")
            return {}

    def calculate_statistics(self, history: List[Dict]) -> Dict:
        """
        Compute statistical summaries (average, min, max) from weather history.

        Args:
            history (List[Dict]): List of processed weather records.

        Returns:
            Dict: Statistics including average, min, max temperature, and trend.
        """
        if not history:
            return {}

        # Extract temperature values from history
        temps = [h['temperature'] for h in history]

        # Determine overall trend (rising, falling, stable)
        trend = self.detect_trend(temps)

        return {
            'average': round(statistics.mean(temps), 1),
            'minimum': min(temps),
            'maximum': max(temps),
            'trend': trend
        }

    @staticmethod
    def detect_trend(temps: List[int]) -> str:
        """
        Determine the trend of temperatures using simple linear regression.

        Args:
            temps (List[int]): List of temperature values.

        Returns:
            str: One of 'rising', 'falling', or 'stable'.
        """
        n = len(temps)
        if n < 2:
            return "stable"  # Not enough data to detect a trend

        # Prepare data for linear regression (x = index, y = temperature)
        x = list(range(n))
        y = temps

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        # Compute slope of best-fit line (simple linear regression)
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        denominator = sum((xi - mean_x) ** 2 for xi in x)

        if denominator == 0:
            return "stable"

        slope = numerator / denominator

        # Interpret slope: small change = stable; otherwise rising/falling
        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "rising"
        else:
            return "falling"

    @staticmethod
    def convert_temperature(temp, from_unit, to_unit):
        """
        Convert temperature between Fahrenheit and Celsius.

        Args:
            temp (float): Temperature to convert.
            from_unit (str): Source unit ('imperial' or 'metric').
            to_unit (str): Target unit ('imperial' or 'metric').

        Returns:
            float: Converted temperature.
        """
        if from_unit == to_unit:
            return temp
        # Convert based on target unit
        return (temp - 32) * 5 / 9 if to_unit == "metric" else (temp * 9 / 5) + 32
