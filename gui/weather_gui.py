import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.api import WeatherAPI
from config import Config
from core.processor import DataProcessor, WeatherDB
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

        tk.Label(top_frame, text="Enter City Name:", font=("Helvetica", 14)).pack(side="left")
        self.city_entry = tk.Entry(top_frame, font=("Helvetica", 14))
        self.city_entry.pack(side="left", padx=5)

        self.unit_var = tk.StringVar(value="imperial")
        unit_dropdown = ttk.OptionMenu(top_frame, self.unit_var, "imperial", "imperial", "metric")
        unit_dropdown.pack(side="left", padx=5)

        tk.Button(top_frame, text="Get Weather", command=self.handle_weather_request, font=("Helvetica", 14)).pack(side="left", padx=5)
        tk.Button(top_frame, text="Switch Theme", command=self.toggle_theme).pack(side="right", padx=5)

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.weather_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=15, pady=15)
        self.weather_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=5)

        self.weather_label = tk.Label(self.weather_frame, text="Weather info will appear here", font=("Helvetica", 14), justify="center")
        self.weather_label.pack(expand=True)

        stats_frame = tk.Frame(main_frame, bd=2, relief="groove")
        stats_frame.pack(side="left", fill="both", expand=True, pady=5)

        self.tab_control = ttk.Notebook(stats_frame)
        self.tab_control.pack(fill="both", expand=True)

        temp_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(temp_tab, text="Temperature Stats")

        self.stats_label = tk.Label(temp_tab, text="Statistics will appear here", font=("Helvetica", 14), justify="center")
        self.stats_label.pack(pady=10)

        self.stats_canvas = tk.Canvas(temp_tab, width=300, height=250, bg="white", bd=1, relief="sunken")
        self.stats_canvas.pack(padx=10, pady=10)

        achievements_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(achievements_tab, text="Achievements")

        self.achievements_text = tk.Text(achievements_tab, state="disabled", width=40, height=15, wrap="word", font=("Helvetica", 12))
        self.achievements_text.pack(padx=10, pady=10, fill="both", expand=True)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", pady=10)
        tk.Button(bottom_frame, text="Export Weather History to CSV", command=self.export_history).pack()

        self.update_achievements_display()
        self.update_statistics()

    def handle_weather_request(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        unit = self.unit_var.get()
        raw_data = self.weather_api.fetch_weather(city, units=unit)
        if raw_data:
            processed = self.processor.process_api_response(raw_data, units=unit)
            if not processed:
                messagebox.showerror("Processing Error", "Weather data format was invalid.")
                return

            self.weather_history.append(processed)
            self.db.save_weather_entry(processed)

            if not self.achievements["first_search"]:
                self.achievements["first_search"] = True
                self.notify_achievement("First search completed!")

            self.searched_cities.add(processed['city'])
            if len(self.searched_cities) >= 5 and not self.achievements["five_cities"]:
                self.achievements["five_cities"] = True
                self.notify_achievement("You have searched for 5 different cities!")

            temp = processed['temperature']
            if (temp >= 100 or temp <= 32) and not self.achievements["temp_extreme"]:
                self.achievements["temp_extreme"] = True
                self.notify_achievement("You discovered an extreme temperature!")

            self.achievements["used_both_units"][unit] = True
            if all(self.achievements["used_both_units"].values()):
                self.notify_achievement("You've used both imperial and metric units!")

            self.save_achievements()
            self.update_achievements_display()

            weather_text = (
                f"{processed['city']}\n"
                f"{processed['description'].title()}\n"
                f"Temp: {processed['temperature']}{processed['unit']}\n"
                f"Feels Like: {processed['feels_like']}{processed['unit']}\n"
                f"Humidity: {processed['humidity']}%\n"
                f"Wind: {processed['wind_speed']}"
            )
            self.weather_label.config(text=weather_text)
            self.update_statistics()
        else:
            messagebox.showerror("Error", "Could not fetch weather data.")

    def update_statistics(self):
        if not self.weather_history:
            self.stats_label.config(text="No statistics available.")
            self.stats_canvas.delete("all")
            return

        stats = self.processor.calculate_statistics(self.weather_history)
        stats_text = (
            f"Average Temp: {stats['average']}°F\n"
            f"Min Temp: {stats['minimum']}°F\n"
            f"Max Temp: {stats['maximum']}°F\n"
            f"Trend: {stats['trend'].capitalize()}"
        )
        self.stats_label.config(text=stats_text)

        self.stats_canvas.delete("all")
        temps = [entry['temperature'] for entry in self.weather_history]
        if not temps:
            return

        max_temp = max(temps)
        min_temp = min(temps)
        width = 300
        height = 250
        bar_width = max(10, width // len(temps))
        margin = 10

        def norm(temp):
            return height - margin - ((temp - min_temp) / (max_temp - min_temp + 1e-5) * (height - 2*margin))

        colors = ["skyblue", "lightgreen", "orange", "violet", "pink", "lightcoral"]

        for i, temp in enumerate(temps):
            x0 = margin + i * bar_width
            y0 = norm(temp)
            x1 = x0 + bar_width - 2
            y1 = height - margin
            color = colors[i % len(colors)]
            self.stats_canvas.create_rectangle(x0, y0, x1, y1, fill=color)
            self.stats_canvas.create_text(x0 + bar_width/2 - 1, y0 - 10, text=str(temp), font=("Helvetica", 9), anchor="s")

    def export_history(self):
        if not self.weather_history:
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
            self.processor.export_to_csv(self.weather_history, file_path)
            messagebox.showinfo("Export", f"Weather history saved to {file_path}")

            if not self.achievements["exported_history"]:
                self.achievements["exported_history"] = True
                self.notify_achievement("You exported your weather history!")
                self.save_achievements()
                self.update_achievements_display()

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.db.save_preference("theme", self.current_theme)

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])
        for widget in self.root.winfo_children():
            self.apply_theme_recursive(widget, theme)

    def apply_theme_recursive(self, widget, theme):
        try:
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        except:
            pass
        if isinstance(widget, tk.Entry):
            widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=theme["button_bg"], fg=theme["button_fg"])
        for child in widget.winfo_children():
            self.apply_theme_recursive(child, theme)

    def save_achievements(self):
        for name, value in self.achievements.items():
            self.db.save_achievement(name, json.dumps(value))

    def load_achievements(self):
        data = self.db.load_achievements()
        for key, val in data.items():
            try:
                self.achievements[key] = json.loads(val)
            except json.JSONDecodeError:
                self.achievements[key] = val

    def update_achievements_display(self):
        unlocked = []
        if self.achievements["first_search"]:
            unlocked.append("🌤 First search completed!")
        if self.achievements["five_cities"]:
            unlocked.append("🌍 Searched 5 different cities")
        if self.achievements["temp_extreme"]:
            unlocked.append("🔥 Discovered extreme temperatures")
        if self.achievements["exported_history"]:
            unlocked.append("💾 Exported weather history")
        if all(self.achievements["used_both_units"].values()):
            unlocked.append("⚖️ Used both imperial and metric")

        self.achievements_text.config(state="normal")
        self.achievements_text.delete("1.0", tk.END)
        self.achievements_text.insert(tk.END, "\n".join(unlocked) if unlocked else "No achievements unlocked yet.")
        self.achievements_text.config(state="disabled")

    def load_theme_preference(self):
        theme = self.db.load_preference("theme")
        if theme in self.themes:
            self.current_theme = theme

    def notify_achievement(self, message):
        messagebox.showinfo("Achievement Unlocked!", message)

    def run(self):
        self.root.mainloop()


# Run the app
if __name__ == "__main__":
    app = WeatherApp()
    app.run()
