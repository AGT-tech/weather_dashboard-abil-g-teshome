import pandas as pd

class Weatherprocessor:
    """Handles weather data processing tasks."""

    def convert_temperature(self, celsius):
        """Convert Celsius to Fahrenheit."""
        return celsius * 1.8 + 32