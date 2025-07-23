import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from core.api import WeatherAPI

from gui.weather_gui import WeatherApp 

def main():
    # Load config from environment variables
    config = Config.from_environment()
    logging.basicConfig(level=getattr(logging, config.log_level.upper(), logging.INFO))

    # Initialize WeatherAPI using config values
    weather_api = WeatherAPI(
        api_key=config.api_key,
        timeout=config.request_timeout
    )
 
if __name__ == "__main__":
    app = WeatherApp()
    app.run()
