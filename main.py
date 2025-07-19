import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from core.api import WeatherAPI

from gui.weather_gui import WeatherApp 

def main():
    # Load config from environment variables
    config = Config.from_environment()

    # Initialize WeatherAPI using config values
    weather_api = WeatherAPI(
        api_key=config.api_key,
        timeout=config.request_timeout
    )

    # Prompt user for a city and fetch weather
    city = input("Enter a city name: ").strip()
    weather_data = weather_api.fetch_weather(city)

    if weather_data:
        print(f"Weather in {city}: {weather_data['weather'][0]['description'].title()}")
        print(f"Temperature: {weather_data['main']['temp']}°F")
    else:
        print("Could not fetch weather data. Please check the city name or try again later.")

if __name__ == "__main__":
    app = WeatherApp()
    app.run()
