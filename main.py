"""
main.py

Entry point for the WeatherApp GUI application. This script:
- Loads configuration from environment variables.
- Sets up application-wide logging.
- Initializes and runs the WeatherApp GUI.
- Handles fatal errors on startup.
"""

import sys
import os

# Add the current directory to sys.path to allow local imports to work correctly,
# regardless of where the script is executed from.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config  # Configuration loader
from utils.logger_config import setup_logging  # Logging setup utility
from gui.weather_gui import WeatherApp  # GUI application class
import logging


def main():
    """
    Main function that bootstraps the WeatherApp GUI.
    Loads configuration, sets up logging, and launches the GUI.
    Handles any exceptions by logging the error and exiting.
    """
    try:
        # Load configuration from environment or defaults
        config = Config.from_environment()

        # Initialize logging using the log level from config
        setup_logging(log_level=config.log_level)

        # Log the start of the application
        logging.getLogger(__name__).info("Starting WeatherApp")

        # Create and run the WeatherApp GUI
        app = WeatherApp()
        app.run()

    except Exception as e:
        # Log any unhandled exceptions that occur during startup
        logging.getLogger(__name__).exception("Fatal error on startup")

        # Exit the application with a non-zero status code to indicate failure
        sys.exit(1)


# Only execute the main function if this script is run directly (not imported)
if __name__ == "__main__":
    main()
