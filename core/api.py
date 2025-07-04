import requests

class WeatherAPI:
    """Basic weahter application with core functionality"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.timeout = 10
        
    

