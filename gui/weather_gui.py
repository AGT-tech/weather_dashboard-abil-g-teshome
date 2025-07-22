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
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("900x600")

        config = Config.from_environment()
        self.weather_api = WeatherAPI(api_key=config.api_key)
        self.processor = DataProcessor()

        self.db = WeatherDB()
        self.weather_history = self.db.get_weather_history()

        self.achievements = {
            "first_search": False,
            "five_cities": False,
            "temp_extreme": False,
            "exported_history": False,
            "used_both_units": {"imperial": False, "metric": False}
        }
        self.searched_cities = set()
        self.load_achievements()

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

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.city_entry = tk.Entry(top_frame, font=("Helvetica", 14))
        self.city_entry.pack(side="left", padx=5)

        # Insert placeholder text and set placeholder color
        self.city_entry.insert(0, "Enter City Name")
        self.city_entry.config(fg="grey")

        # Bind focus and keyboard events
        self.city_entry.bind("<FocusIn>", self.clear_placeholder)
        self.city_entry.bind("<FocusOut>", self.restore_placeholder)
        self.city_entry.bind("<Return>", self.enter_pressed)

        self.unit_var = tk.StringVar(value="imperial")
        unit_dropdown = ttk.OptionMenu(top_frame, self.unit_var, "imperial", "imperial", "metric")
        unit_dropdown.pack(side="left", padx=5)

        fetch_btn = tk.Button(top_frame, text="Get Weather", command=self.handle_weather_request, font=("Helvetica", 14))
        fetch_btn.pack(side="left", padx=5)

        theme_btn = tk.Button(top_frame, text="Switch Theme", command=self.toggle_theme)
        theme_btn.pack(side="right", padx=5)

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

        history_frame = tk.Frame(self.root, bd=2, relief="groove", padx=15, pady=15)
        history_frame.pack(fill="x", padx=10, pady=10)

        history_label = tk.Label(history_frame, text="Search History", font=("Helvetica", 16, "bold"))
        history_label.pack(anchor="w")

        self.history_listbox = tk.Listbox(history_frame, height=6, font=("Helvetica", 12))
        self.history_listbox.pack(fill="x")
        self.update_history_display()

        export_btn = tk.Button(self.root, text="Export History to CSV", command=self.export_history)
        export_btn.pack(pady=10)

        achievements_frame = tk.Frame(self.root, bd=2, relief="groove", padx=15, pady=15)
        achievements_frame.pack(fill="x", padx=10, pady=10)

        ach_label = tk.Label(achievements_frame, text="Achievements", font=("Helvetica", 16, "bold"))
        ach_label.pack(anchor="w")

        self.achievements_listbox = tk.Listbox(achievements_frame, height=6, font=("Helvetica", 12))
        self.achievements_listbox.pack(fill="x")
        self.update_achievements_display()

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

    def handle_weather_request(self):
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
        self.db.save_weather_entry(data)
        self.weather_history = self.db.get_weather_history()

    def update_statistics(self):
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

        # Draw trend label
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
            filetypes=[("CSV files", "*.csv")],
            title="Save Weather History"
        )

        if file_path:
            self.db.export_to_csv(file_path)
            messagebox.showinfo("Export", f"Weather history saved to {file_path}")

            if not self.achievements["exported_history"]:
                self.achievements["exported_history"] = True
                self.notify_achievement("You exported your weather history!")
                self.save_achievements()
                self.update_achievements_display()

    def check_achievements(self, data, city, units):
        updated = False

        if not self.achievements["first_search"]:
            self.achievements["first_search"] = True
            self.notify_achievement("First search done!")
            updated = True

        self.searched_cities.add(city.lower())
        if not self.achievements["five_cities"] and len(self.searched_cities) >= 5:
            self.achievements["five_cities"] = True
            self.notify_achievement("Searched five different cities!")
            updated = True

        if not self.achievements["temp_extreme"] and (data['temperature'] >= 90 or data['temperature'] <= 32):
            self.achievements["temp_extreme"] = True
            self.notify_achievement("Extreme temperature reached!")
            updated = True

        # Track unit usage
        if not self.achievements["used_both_units"].get(units, False):
            self.achievements["used_both_units"][units] = True
            if all(self.achievements["used_both_units"].values()):
                self.notify_achievement("Used both imperial and metric units!")
                updated = True

        if updated:
            self.save_achievements()
            self.update_achievements_display()

    def notify_achievement(self, message):
        messagebox.showinfo("Achievement Unlocked!", message)

    def save_achievements(self):
        # Save to DB
        for key, val in self.achievements.items():
            if isinstance(val, dict):
                self.db.save_achievement(key, json.dumps(val))
            else:
                self.db.save_achievement(key, json.dumps(val))

    def load_achievements(self):
        loaded = self.db.load_achievements()
        for key, val in loaded.items():
            try:
                parsed = json.loads(val)
                self.achievements[key] = parsed
            except Exception:
                self.achievements[key] = val

    def update_achievements_display(self):
        self.achievements_listbox.delete(0, tk.END)
        for ach, unlocked in self.achievements.items():
            status = "✓" if unlocked else "✗"
            if isinstance(unlocked, dict):
                # For used_both_units dict, check if both true
                status = "✓" if all(unlocked.values()) else "✗"
            self.achievements_listbox.insert(tk.END, f"{status} {ach.replace('_', ' ').title()}")

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.db.save_preference("theme", self.current_theme)

    def load_theme_preference(self):
        saved = self.db.load_preference("theme")
        if saved in self.themes:
            self.current_theme = saved

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])

        # Apply colors recursively
        def recursive_apply(widget):
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(bg=theme["bg"])
                    recursive_apply(child)
                elif isinstance(child, tk.Label):
                    child.configure(bg=theme["bg"], fg=theme["fg"])
                elif isinstance(child, tk.Button):
                    child.configure(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
                elif isinstance(child, tk.Entry):
                    child.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["fg"])
                elif isinstance(child, tk.Listbox):
                    child.configure(bg=theme["entry_bg"], fg=theme["entry_fg"])
                elif isinstance(child, ttk.OptionMenu):
                    # ttk widgets don't support bg directly; skip or style differently if desired
                    pass
                else:
                    recursive_apply(child)
        recursive_apply(self.root)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
