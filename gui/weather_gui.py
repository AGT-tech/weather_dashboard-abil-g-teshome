import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.api import WeatherAPI
from config import Config
from core.processor import DataProcessor
from core.storage import WeatherDB
from datetime import datetime
import os
import json


class WeatherApp:
    def __init__(self):
        """
        Initialize the WeatherApp GUI, load configuration, API, processor,
        database, achievements, theme preferences, and setup the UI.
        """
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("900x600")

        config = Config.from_environment()
        self.weather_api = WeatherAPI(api_key=config.api_key)
        self.processor = DataProcessor()

        self.db = WeatherDB()
        self.weather_history = self.db.get_weather_history()

        # Track achievements and user progress
        self.achievements = {
            "first_search": False,
            "five_cities": False,
            "temp_extreme": False,
            "exported_history": False,
            "used_both_units": {"imperial": False, "metric": False}
        }
        self.searched_cities = set()
        self.load_achievements()

        # Theme setup with light/dark options
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#FFFFFF", "fg": "#000000",
                "entry_bg": "#FFFFFF", "entry_fg": "#000000",
                "button_bg": "#E0E0E0", "button_fg": "#000000"
            },
            "dark": {
                "bg": "#2E2E2E", "fg": "#FFFFFF",
                "entry_bg": "#3C3F41", "entry_fg": "#FFFFFF",
                "button_bg": "#555555", "button_fg": "#FFFFFF"
            }
        }
        self.load_theme_preference()

        # Build and display the UI
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Create and place all UI components/widgets in the main window."""
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.city_entry = tk.Entry(top_frame, font=("Helvetica", 14))
        self.city_entry.pack(side="left", padx=5)

        # Insert placeholder text and set placeholder color
        self.city_entry.insert(0, "Enter City Name")
        self.city_entry.config(fg="grey")

        # Bind focus and keyboard events to handle placeholder and enter key
        self.city_entry.bind("<FocusIn>", self.clear_placeholder)
        self.city_entry.bind("<FocusOut>", self.restore_placeholder)
        self.city_entry.bind("<Return>", self.enter_pressed)

        # Dropdown for units (imperial or metric)
        self.unit_var = tk.StringVar(value="imperial")
        unit_dropdown = ttk.OptionMenu(top_frame, self.unit_var, "imperial", "imperial", "metric")
        unit_dropdown.pack(side="left", padx=5)

        fetch_btn = tk.Button(top_frame, text="Get Weather", command=self.handle_weather_request, font=("Helvetica", 14))
        fetch_btn.pack(side="left", padx=5)

        theme_btn = tk.Button(top_frame, text="Switch Theme", command=self.toggle_theme)
        theme_btn.pack(side="right", padx=5)

        # Main frames for weather display and statistics
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.weather_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=15, pady=15)
        self.weather_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        self.weather_label = tk.Label(self.weather_frame, text="Weather info will appear here", font=("Helvetica", 14), justify="center")
        self.weather_label.pack(expand=True)

        stats_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=15, pady=15)
        stats_frame.pack(side="left", fill="both", expand=True, pady=5)

        stats_label = tk.Label(stats_frame, text="Statistics", font=("Helvetica", 16, "bold"))
        stats_label.pack()

        self.stats_label = tk.Label(stats_frame, text="No data yet", font=("Helvetica", 14))
        self.stats_label.pack(pady=5)

        self.stats_canvas = tk.Canvas(stats_frame, height=100)
        self.stats_canvas.pack(fill="x")

        # History frame showing past searches
        history_frame = tk.Frame(self.root, bd=2, relief="groove", padx=15, pady=15)
        history_frame.pack(fill="x", padx=10, pady=10)

        history_label = tk.Label(history_frame, text="Search History", font=("Helvetica", 16, "bold"))
        history_label.pack(anchor="w")

        self.history_listbox = tk.Listbox(history_frame, height=6, font=("Helvetica", 12))
        self.history_listbox.pack(fill="x")
        self.update_history_display()

        export_btn = tk.Button(self.root, text="Export History to CSV", command=self.export_history)
        export_btn.pack(pady=10)

        # Achievements frame
        achievements_frame = tk.Frame(self.root, bd=2, relief="groove", padx=15, pady=15)
        achievements_frame.pack(fill="x", padx=10, pady=10)

        ach_label = tk.Label(achievements_frame, text="Achievements", font=("Helvetica", 16, "bold"))
        ach_label.pack(anchor="w")

        self.achievements_listbox = tk.Listbox(achievements_frame, height=6, font=("Helvetica", 12))
        self.achievements_listbox.pack(fill="x")
        self.update_achievements_display()

    def clear_placeholder(self, event):
        """Clear placeholder text when the entry field gains focus."""
        if self.city_entry.get() == "Enter City Name":
            self.city_entry.delete(0, "end")
            self.city_entry.config(fg="black")

    def restore_placeholder(self, event):
        """Restore placeholder text if entry is empty when it loses focus."""
        if not self.city_entry.get():
            self.city_entry.insert(0, "Enter City Name")
            self.city_entry.config(fg="grey")

    def enter_pressed(self, event):
        """Handle Enter key press event to trigger weather request."""
        self.handle_weather_request()

    def handle_weather_request(self):
        """
        Fetch weather data from API for the city entered, process and display it,
        update history, statistics, and check for any new achievements.
        """
        city = self.city_entry.get().strip()
        if not city or city == "Enter City Name":
            messagebox.showerror("Error", "Please enter a city name.")
            return

        units = self.unit_var.get()
        data = self.weather_api.fetch_weather(city, units)

        if data is None or "main" not in data:
            messagebox.showerror("Error", "Could not fetch weather data. Please check the city name or try again.")
            return

        processed = self.processor.process_api_response(data, units)
        if not processed:
            messagebox.showerror("Error", "Error processing weather data.")
            return

        self.display_weather(processed)
        self.save_weather_entry(processed)
        self.update_statistics()
        self.update_history_display()
        self.check_achievements(processed, city, units)

    def display_weather(self, data):
        """Update the weather display label with the current data."""
        text = (
            f"{data['temperature']}{data['unit']}\n"
            f"{data['city']}\n"
            f"Feels Like: {data['feels_like']}{data['unit']}\n"
            f"Humidity: {data['humidity']}%\n"
            f"Description: {data['description'].capitalize()}\n"
            f"Wind Speed: {data['wind_speed']}"
        )
        self.weather_label.config(text=text)

    def save_weather_entry(self, data):
        """Save the current weather data entry into the database and refresh history."""
        self.db.save_weather_entry(data)
        self.weather_history = self.db.get_weather_history()

    def update_statistics(self):
        """
        Calculate statistics from the weather history and update the display,
        including drawing the temperature trend graph.
        """
        history = self.db.get_weather_history()
        if not history:
            self.stats_label.config(text="No statistics available.")
            self.stats_canvas.delete("all")
            return

        stats = self.processor.calculate_statistics(history)
        text = (
            f"Average Temp: {stats['average']}\n"
            f"Min Temp: {stats['minimum']}\n"
            f"Max Temp: {stats['maximum']}\n"
            f"Trend: {stats['trend']}"
        )
        self.stats_label.config(text=text)
        self.draw_trend_graph(history, stats['trend'])

    def draw_trend_graph(self, history, trend):
        """Draw a line graph of temperature trend on the statistics canvas."""
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
            self.stats_canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill="blue", width=2)

        # Draw trend label at top right corner
        self.stats_canvas.create_text(width - 50, 10, text=trend.capitalize(), fill="black", font=("Helvetica", 12, "bold"))

    def update_history_display(self):
        """Refresh the search history listbox with recent entries."""
        self.history_listbox.delete(0, tk.END)
        for entry in self.weather_history:
            line = f"{entry['timestamp'][:19]} - {entry['city']} - {entry['temperature']}{entry['unit']}"
            self.history_listbox.insert(tk.END, line)

    def export_history(self):
        """
        Export weather search history to a CSV file selected by the user.
        Unlock the export achievement if not already unlocked.
        """
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
            return  # User cancelled save dialog

        try:
            self.db.export_to_csv(file_path)
            messagebox.showinfo("Export", f"History exported to {file_path}")

            # Unlock achievement if not already unlocked
            if not self.achievements["exported_history"]:
                self.achievements["exported_history"] = True
                self.save_achievements()
                self.update_achievements_display()
                messagebox.showinfo("Achievement Unlocked", "Exported your search history!")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export history: {e}")

    def toggle_theme(self):
        """Switch between light and dark theme and save the preference."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_theme_preference()

    def apply_theme(self):
        """Apply the current theme colors to all UI widgets."""
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])

        # Update colors for all children recursively
        def recursive_color_update(widget):
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame) or isinstance(child, tk.LabelFrame):
                    child.configure(bg=theme["bg"])
                elif isinstance(child, tk.Label):
                    child.configure(bg=theme["bg"], fg=theme["fg"])
                elif isinstance(child, tk.Button):
                    child.configure(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
                elif isinstance(child, tk.Entry):
                    child.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])
                elif isinstance(child, tk.Listbox):
                    child.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], selectbackground="#6A95FF")
                elif isinstance(child, tk.Canvas):
                    child.configure(bg=theme["bg"])
                recursive_color_update(child)

        recursive_color_update(self.root)

    def load_theme_preference(self):
        """Load the saved theme preference from a file, if it exists."""
        try:
            with open("data/theme_pref.json", "r") as f:
                data = json.load(f)
                if data.get("theme") in self.themes:
                    self.current_theme = data["theme"]
        except FileNotFoundError:
            # Default theme is light if no preference saved
            self.current_theme = "light"

    def save_theme_preference(self):
        """Save the current theme preference to a file."""
        os.makedirs("data", exist_ok=True)
        with open("data/theme_pref.json", "w") as f:
            json.dump({"theme": self.current_theme}, f)

    def load_achievements(self):
        """Load achievements from a saved file, or initialize fresh achievements."""
        try:
            with open("data/achievements.json", "r") as f:
                saved = json.load(f)
                for key in self.achievements:
                    if key in saved:
                        self.achievements[key] = saved[key]
        except FileNotFoundError:
            # No saved achievements yet, start fresh
            pass

    def save_achievements(self):
        """Save the current achievements state to a file."""
        os.makedirs("data", exist_ok=True)
        with open("data/achievements.json", "w") as f:
            json.dump(self.achievements, f)

    def update_achievements_display(self):
        """Refresh the achievements listbox to show unlocked achievements."""
        self.achievements_listbox.delete(0, tk.END)
        achievement_texts = {
            "first_search": "First Search Completed",
            "five_cities": "Searched 5 Different Cities",
            "temp_extreme": "Encountered Temperature Extremes",
            "exported_history": "Exported Search History",
            "used_both_units": "Used Both Imperial and Metric Units"
        }
        for key, unlocked in self.achievements.items():
            if key == "used_both_units":
                # Check if both units used
                if unlocked["imperial"] and unlocked["metric"]:
                    self.achievements_listbox.insert(tk.END, achievement_texts[key])
            elif unlocked:
                self.achievements_listbox.insert(tk.END, achievement_texts[key])

    def check_achievements(self, data, city, units):
        """
        Check if the user unlocked any new achievements based on current search.
        Update achievements and notify the user if unlocked.
        """
        unlocked_new = False

        # Achievement: First search
        if not self.achievements["first_search"]:
            self.achievements["first_search"] = True
            unlocked_new = True

        # Achievement: Searched 5 different cities
        self.searched_cities.add(city.lower())
        if not self.achievements["five_cities"] and len(self.searched_cities) >= 5:
            self.achievements["five_cities"] = True
            unlocked_new = True

        # Achievement: Encountered extreme temperatures (below 0 or above 100 F / 37.8 C)
        temp = data["temperature"]
        if units == "imperial":
            if not self.achievements["temp_extreme"] and (temp < 0 or temp > 100):
                self.achievements["temp_extreme"] = True
                unlocked_new = True
        else:
            if not self.achievements["temp_extreme"] and (temp < -17.8 or temp > 37.8):
                self.achievements["temp_extreme"] = True
                unlocked_new = True

        # Achievement: Used both units
        self.achievements["used_both_units"][units] = True
        if self.achievements["used_both_units"]["imperial"] and self.achievements["used_both_units"]["metric"]:
            # Already handled in display, just save
            pass

        if unlocked_new:
            self.save_achievements()
            self.update_achievements_display()
            messagebox.showinfo("Achievement Unlocked!", "You unlocked a new achievement!")

    def run(self):
        """Start the Tkinter main event loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
