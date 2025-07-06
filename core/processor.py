# core/processor.py
"""Data processing module"""

from typing import Dict, List
import statistics

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
        
        return {
            'average': round(statistics.mean(temps), 1),
            'minimum': min(temps),
            'maximum': max(temps),
            'trend': 'rising' if temps[-1] > temps[0] else 'falling'
        }