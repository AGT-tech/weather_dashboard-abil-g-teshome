import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.api import WeatherAPI
from config import Config
from core.processor import DataProcessor
from core.storage import WeatherDB
from features.statistics_manager import StatisticsManager
from features.theme_manager import ThemeManager
from features.trend_manager import TrendDetector
from features.achievement_manager import AchievementManager
from datetime import datetime
from PIL import Image, ImageTk
import os
import logging


class WeatherApp:
    def __init__(self):
        """Initialize the WeatherApp GUI and all supporting components."""
        self.logger = logging.getLogger(__name__)  # logger setup

        self.root = tk.Tk()
        self.root.configure(bg="orange")
        self.root.title("Weather Dashboard")
        self.root.geometry("900x600")

        config = Config.from_environment()
        self.weather_api = WeatherAPI(
            api_key=config.api_key,
            timeout=config.request_timeout
        )
        self.processor = DataProcessor()
        self.theme_manager = ThemeManager(self.root)
        self.db = WeatherDB()
        self.weather_history = self.db.get_weather_history()
        self.searched_cities = set()

        self.setup_ui()
        self.theme_manager.apply_theme()

    def setup_ui(self):
        self.setup_top_frame()
        self.setup_main_frame()
        self.setup_history_frame()
        self.setup_achievements_frame()

    def setup_top_frame(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.city_entry = tk.Entry(top_frame, font=("Helvetica", 14))
        self.city_entry.pack(side="left", padx=5)
        self.city_entry.insert(0, "Enter City Name")
        self.city_entry.config(fg="grey")
        self.city_entry.bind("<FocusIn>", self.clear_placeholder)
        self.city_entry.bind("<FocusOut>", self.restore_placeholder)
        self.city_entry.bind("<Return>", self.enter_pressed)

        self.unit_var = tk.StringVar(value="imperial")
        unit_dropdown = ttk.OptionMenu(top_frame, self.unit_var, "imperial", "imperial", "metric")
        unit_dropdown.pack(side="left", padx=5)

        fetch_btn = tk.Button(top_frame, text="Get Weather", command=self.handle_weather_request, font=("Helvetica", 14))
        fetch_btn.pack(side="left", padx=5)

        theme_btn = tk.Button(top_frame, text="Switch Theme", command=self.theme_manager.toggle_theme)
        theme_btn.pack(side="right", padx=5)

    def setup_main_frame(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.weather_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=15, pady=15)
        self.weather_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        self.temperature_label = tk.Label(self.weather_frame, text="", font=("Helvetica", 70, "bold"), justify="center")
        self.temperature_label.pack()

        self.icon_label = tk.Label(self.weather_frame)
        self.icon_label.pack()

        self.weather_info_label = tk.Label(self.weather_frame, text="Weather info will appear here", font=("Helvetica", 14), justify="center")
        self.weather_info_label.pack(expand=True)

        stats_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=15, pady=15)
        stats_frame.pack(side="left", fill="both", expand=True, pady=5)

        stats_label = tk.Label(stats_frame, text="Statistics", font=("Helvetica", 16, "bold"))
        stats_label.pack()

        self.stats_label = tk.Label(stats_frame, text="No data yet", font=("Helvetica", 14))
        self.stats_label.pack(pady=5)

        self.stats_canvas = tk.Canvas(stats_frame, height=100)
        self.stats_canvas.pack(fill="x")

    def setup_history_frame(self):
        history_frame = tk.Frame(self.root, bd=2, relief="groove", padx=15, pady=15)
        history_frame.pack(fill="x", padx=10, pady=10)

        history_label = tk.Label(history_frame, text="Search History", font=("Helvetica", 16, "bold"))
        history_label.pack(anchor="w")

        self.history_listbox = tk.Listbox(history_frame, height=6, font=("Helvetica", 12))
        self.history_listbox.pack(fill="x")
        self.update_history_display()

        export_btn = tk.Button(self.root, text="Export History to CSV", command=self.export_history)
        export_btn.pack(pady=10)

    def setup_achievements_frame(self):
        achievements_frame = tk.Frame(self.root, bd=2, relief="groove", padx=15, pady=15)
        achievements_frame.pack(fill="x", padx=10, pady=10)

        ach_label = tk.Label(achievements_frame, text="Achievements", font=("Helvetica", 16, "bold"))
        ach_label.pack(anchor="w")

        self.achievements_listbox = tk.Listbox(achievements_frame, height=6, font=("Helvetica", 12))
        self.achievements_listbox.pack(fill="x")

        self.achievement_manager = AchievementManager(
            self.achievements_listbox,
            self.searched_cities
        )

    def clear_placeholder(self, event):
        if self.city_entry.get() == "Enter City Name":
            self.city_entry.delete(0, "end")
            self.city_entry.config(fg="black")

    def restore_placeholder(self, event):
        if not self.city_entry.get():
            self.city_entry.insert(0, "Enter City Name")
            self.city_entry.config(fg="grey")

    def enter_pressed(self, event):
        self.handle_weather_request()

    def get_valid_city(self):
        city = self.city_entry.get().strip()
        if not city or city == "Enter City Name":
            self.show_error("Please enter a city name.")
            return None
        return city

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def handle_weather_request(self):
        city = self.get_valid_city()
        if city is None:
            return

        units = self.unit_var.get()
        self.logger.info(f"Fetching weather for: {city} ({units})")

        data, error = self.weather_api.fetch_weather(city, units)

        if error:
            self.logger.warning(f"Weather API error: {error}")
            self.show_error(error)
            return

        if not data or "main" not in data:
            self.logger.error("Invalid response from API.")
            self.show_error("Could not fetch weather data.")
            return

        processed = self.processor.process_api_response(data, units)
        if not processed:
            self.logger.error("Processing weather data failed.")
            self.show_error("Error processing weather data.")
            return

        self.logger.debug(f"Processed data: {processed}")
        self.update_ui_with_weather(processed, city, units)

    def update_ui_with_weather(self, processed, city, units):
        self.display_weather(processed)
        self.save_weather_entry(processed)
        self.update_statistics()
        self.update_history_display()
        self.achievement_manager.check_achievements(processed, city, units)

    def display_weather(self, data):
        self.temperature_label.config(text=f"{data['temperature']}{data['unit']}")

        info_text = (
            f"{data['city']}\n"
            f"Feels Like: {data['feels_like']}{data['unit']}\n"
            f"Humidity: {data['humidity']}%\n"
            f"Description: {data['description'].capitalize()}\n"
            f"Wind Speed: {data['wind_speed']}"
        )
        self.weather_info_label.config(text=info_text)

        icon_path = self.get_weather_icon_path(data["description"])

        try:
            img = Image.open(icon_path).resize((64, 64), Image.ANTIALIAS)
            self.weather_icon = ImageTk.PhotoImage(img)
            self.icon_label.config(image=self.weather_icon)
        except Exception as e:
            self.logger.warning(f"Failed to load weather icon: {e}")
            self.icon_label.config(image="")

    def get_weather_icon_path(self, description):
        mapping = {
            "clear": "clear.png",
            "clouds": "clouds.png",
            "rain": "rain.png",
            "drizzle": "drizzle.png",
            "thunderstorm": "thunderstorm.png",
            "snow": "snow.png",
            "mist": "mist.png",
        }
        desc = description.lower()
        for key in mapping:
            if key in desc:
                icon_filename = mapping[key]
                break
        else:
            icon_filename = "default.png"

        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "assets", "icons", icon_filename)

    def save_weather_entry(self, data):
        self.db.save_weather_entry(data)
        self.weather_history = self.db.get_weather_history()

    def update_statistics(self):
        history = self.db.get_weather_history()
        if not history:
            self.stats_label.config(text="No statistics available.")
            self.stats_canvas.delete("all")
            return

        stats = StatisticsManager.calculate_statistics(history)
        temps = [entry['temperature'] for entry in history]
        trend = TrendDetector.detect_trend(temps)

        text = (
            f"Average Temp: {stats['average']}\n"
            f"Min Temp: {stats['minimum']}\n"
            f"Max Temp: {stats['maximum']}\n"
            f"Trend: {trend.capitalize()}"
        )
        self.stats_label.config(text=text)
        self.draw_trend_graph(history, trend)

    def draw_trend_graph(self, history, trend):
        self.stats_canvas.delete("all")
        temps = [h['temperature'] for h in history]
        if not temps:
            return

        width = self.stats_canvas.winfo_width() or 300
        height = self.stats_canvas.winfo_height() or 100
        max_temp = max(temps)
        min_temp = min(temps)
        temp_range = max_temp - min_temp or 1

        points = []
        for i, t in enumerate(temps):
            x = i * (width / max(len(temps) - 1, 1))
            y = height - ((t - min_temp) / temp_range * height)
            points.append((x, y))

        for i in range(len(points) - 1):
            self.stats_canvas.create_line(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1], fill="blue", width=2)

        self.stats_canvas.create_text(width - 50, 10, text=trend.capitalize(), fill="black", font=("Helvetica", 12, "bold"))

    def update_history_display(self):
        self.history_listbox.delete(0, tk.END)
        for entry in self.weather_history:
            line = f"{entry['timestamp'][:19]} - {entry['city']} - {entry['temperature']}{entry['unit']}"
            self.history_listbox.insert(tk.END, line)

    def export_history(self):
        if not self.db.get_weather_history():
            messagebox.showinfo("Export", "No data to export.")
            return

        os.makedirs("data", exist_ok=True)
        default_filename = f"weather_{datetime.now().strftime('%Y-%m-%d')}.csv"
        file_path = filedialog.asksaveasfilename(
            initialdir=os.path.abspath("data"),
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return

        try:
            self.db.export_to_csv(file_path)
            self.logger.info(f"Exported history to: {file_path}")
            messagebox.showinfo("Export", f"History exported to {file_path}")
            self.achievement_manager.export_achievement()
        except Exception as e:
            self.logger.exception(f"Export failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export history: {e}")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
