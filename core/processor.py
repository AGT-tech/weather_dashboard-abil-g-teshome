# core/processor.py
"""Data processing module"""

from typing import Dict, List
import statistics
# from collections import Counter

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
                'wind_speed': f"{data.get('wind', {}).get('speed', 0)}{wind_unit}",
                "unit": unit_symbol
            }
        except (KeyError, IndexError, TypeError) as e:
            print (f"Error processing data: {e}")
            return {}
    
    def calculate_statistics(self, history: List[Dict]) -> Dict:
        """Calculate statistics from weather history"""
        if not history:
            return {}
            
        temps = [h['temperature'] for h in history]
        # descriptions = [h['desctiption'] for h in history]
        # trend = self.detect_trend(temps)
        
        return {
            'average': round(statistics.mean(temps), 1),
            'minimum': min(temps),
            'maximum': max(temps),
            'trend': 'rising' if temps[-1] > temps[0] else 'falling' #trend,
            # 'weather_counts': dict(Counter(descriptions))
        }
    
    # convert temperature
    def convert_temperature(temp, from_unit, to_unit):
        if from_unit == to_unit:
            return temp
        return (temp- 32) * 5/ 9 if to_unit == "metric" else (temp * 9/5) + 32
    
    def export_to_csv(self, history, file_path=""):
        # importing csv
        import csv
        keys = history[0].keys()
        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(history)
    