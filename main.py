# main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from utils.logger_config import setup_logging
from gui.weather_gui import WeatherApp
import logging

def main():
    config = Config.from_environment()
    setup_logging(log_level=config.log_level)

    logging.getLogger(__name__).info("Starting WeatherApp")

    app = WeatherApp()
    app.run()

if __name__ == "__main__":
    main()
