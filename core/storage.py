import api

class WeatherStorage:
    """Handles saving weather data to a file."""

    def save_weather(self, city, temp):
        with open("data.txt", "a") as f:
            f.write(f"{city}, {temp}\n")

