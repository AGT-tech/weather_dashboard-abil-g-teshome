import tkinter as tk
from tkinter import messagebox
from core.api import WeatherAPI
from config import Config
from core.processor import DataProcessor

class WeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("800x500")

        # Load config and create WeatherAPI instance
        config = Config.from_environment()
        self.weather_api = WeatherAPI(api_key=config.api_key) # timeout=config.request_timeout)

         # Instantiate WeatherProcessor
        self.processor = DataProcessor()
        self.weather_history = []

        # Setup UI
        self.setup_ui()


    def setup_ui(self):
        # City input
        tk.Label(self.root, text="Enter City Name:", font=("Helvetica", 14)).pack(pady=10)
        self.city_entry = tk.Entry(self.root, font=("Helvetica", 14))
        self.city_entry.pack(pady=5)

        # Unit selection dropdown
        self.unit_var = tk.StringVar(value="imperial")
        unit_dropdown = tk.OptionMenu(self.root, self.unit_var, "imperial", "metric")
        unit_dropdown.pack(pady=5)

        # Fetch button
        fetch_btn = tk.Button(self.root, text="Get Weather", command=self.handle_weather_request, font=("Helvetica", 14))
        fetch_btn.pack(pady=10)

        # Result display label
        self.result_label = tk.Label(self.root, text="", font=("Helvetica", 12), wraplength=350, justify="center")
        self.result_label.pack(pady=20)

        # Stats button
        stats_btn = tk.Button(self.root, text="Show Stats", command=self.show_statistics)
        stats_btn.pack(pady=5)

    def handle_weather_request(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        unit = self.unit_var.get()
        raw_data = self.weather_api.fetch_weather(city, units=unit)
        if raw_data:
            processed = self.processor.process_api_response(raw_data)

            self.weather_history.append(processed)  # Track history for stats

            unit_symbol = "°F" if unit == "imperial" else "°C"
            self.result_label.config(text=(
                f"{processed['city']}:\n"
                f"{processed['description'].title()}\n"
                f"Temp: {processed['temperature']}{processed['unit']}\n"
                f"Feels Like: {processed['feels_like']}{processed['unit']}\n"
                f"Humidity: {processed['humidity']}%\n"
                f"Wind: {processed['wind_speed']} mph"
        ))

        else:
            messagebox.showerror("Error", "Could not fetch weather data.")

    def show_statistics(self):
        if not self.weather_history:
            messagebox.showinfo("Stats", "No data to analyze.")
            return

        stats = self.processor.calculate_statistics(self.weather_history)
        messagebox.showinfo("Temperature Stats", (
            f"Average: {stats['average']}°F\n"
            f"Min: {stats['minimum']}°F\n"
            f"Max: {stats['maximum']}°F\n"
            f"Trend: {stats['trend'].capitalize()}"
        ))


    def run(self):
        self.root.mainloop()


# Run the app
if __name__ == "__main__":
    app = WeatherApp()
    app.run()


