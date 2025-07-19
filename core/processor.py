# core/processor.py
"""Data processing module"""

from typing import Dict, List
import statistics
# from collections import Counter

class DataProcessor:
    """Processes and analyzes weather data"""
    
    def process_api_response(self, data: Dict) -> Dict:
        """Convert API response to internal format"""
        if not data:
            return {}
            
        return {
            'city': data.get('name', 'Unknown'),
            'temperature': round(data.get('main', {}).get('temp', 0)),
            'feels_like': round(data.get('main', {}).get('feels_like', 0)),
            'humidity': data.get('main', {}).get('humidity', 0),
            'description': data.get('weather', [{}])[0].get('description', ''),
            'wind_speed': data.get('wind', {}).get('speed', 0)
        }
    
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
    def conver_temperature(temp, from_unit, to_unit):
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
    