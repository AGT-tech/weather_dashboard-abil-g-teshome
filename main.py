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

    # Set up logging once here
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logging.info("Starting WeatherApp")

    # Initialize WeatherAPI using config values
    weather_api = WeatherAPI(
        api_key=config.api_key,
        timeout=config.request_timeout
    )

    # Initialize and run the GUI app
    app = WeatherApp()
    app.run()

if __name__ == "__main__":
    main()    
