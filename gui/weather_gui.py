import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.api import WeatherAPI
from config import Config
from core.processor import DataProcessor
from datetime import datetime
import os
import json

class WeatherApp:
    ACHIEVEMENTS_FILE = "achievements.json"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("900x600")

        # Load config and create WeatherAPI instance
        config = Config.from_environment()
        self.weather_api = WeatherAPI(api_key=config.api_key)

        # Instantiate WeatherProcessor
        self.processor = DataProcessor()
        self.weather_history = []

        # Theme handling
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#FFFFFF",
                "fg": "#000000",
                "entry_bg": "#FFFFFF",
                "entry_fg": "#000000",
                "button_bg": "#E0E0E0",
                "button_fg": "#000000"
            },
            "dark": {
                "bg": "#2E2E2E",
                "fg": "#FFFFFF",
                "entry_bg": "#3C3F41",
                "entry_fg": "#FFFFFF",
                "button_bg": "#555555",
                "button_fg": "#FFFFFF"
            }
        }

        self.load_theme_preference()

        # Achievement tracking
        self.achievements = {
            "first_search": False,
            "five_cities": False,
            "temp_extreme": False,
            "exported_history": False,
            "used_both_units": {"imperial": False, "metric": False}
        }
        self.searched_cities = set()
        self.load_achievements()

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        # Top frame for city input, unit selector, theme switcher
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(top_frame, text="Enter City Name:", font=("Helvetica", 14)).pack(side="left")
        self.city_entry = tk.Entry(top_frame, font=("Helvetica", 14))
        self.city_entry.pack(side="left", padx=5)

        self.unit_var = tk.StringVar(value="imperial")
        unit_dropdown = ttk.OptionMenu(top_frame, self.unit_var, "imperial", "imperial", "metric")
        unit_dropdown.pack(side="left", padx=5)

        fetch_btn = tk.Button(top_frame, text="Get Weather", command=self.handle_weather_request, font=("Helvetica", 14))
        fetch_btn.pack(side="left", padx=5)

        # Theme switcher on far right
        theme_btn = tk.Button(top_frame, text="Switch Theme", command=self.toggle_theme)
        theme_btn.pack(side="right", padx=5)

        # Main content frame with weather output and stats side-by-side
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Weather output frame
        self.weather_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=15, pady=15)
        self.weather_frame.pack(side="left", fill="both", expand=True, padx=(0,10), pady=5)

        self.weather_label = tk.Label(self.weather_frame, text="Weather info will appear here", font=("Helvetica", 14), justify="center")
        self.weather_label.pack(expand=True)

        # Stats with tabs frame
        stats_frame = tk.Frame(main_frame, bd=2, relief="groove")
        stats_frame.pack(side="left", fill="both", expand=True, pady=5)

        self.tab_control = ttk.Notebook(stats_frame)
        self.tab_control.pack(fill="both", expand=True)

        # Tab 1 - Temperature Stats
        temp_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(temp_tab, text="Temperature Stats")

        self.stats_label = tk.Label(temp_tab, text="Statistics will appear here", font=("Helvetica", 14), justify="center")
        self.stats_label.pack(pady=10)

        self.stats_canvas = tk.Canvas(temp_tab, width=300, height=250, bg="white", bd=1, relief="sunken")
        self.stats_canvas.pack(padx=10, pady=10)

        # Tab 2 - Achievements
        achievements_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(achievements_tab, text="Achievements")

        self.achievements_text = tk.Text(achievements_tab, state="disabled", width=40, height=15, wrap="word", font=("Helvetica", 12))
        self.achievements_text.pack(padx=10, pady=10, fill="both", expand=True)

        # Export button at bottom centered
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", pady=10)
        export_btn = tk.Button(bottom_frame, text="Export Weather History to CSV", command=self.export_history)
        export_btn.pack()

        # Initial achievements display update
        self.update_achievements_display()

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

            # Achievements logic
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
            try:
                self.processor.export_to_csv(self.weather_history, file_path)
                messagebox.showinfo("Export Successful", f"Weather history saved to:\n{file_path}")

                if not self.achievements["exported_history"]:
                    self.achievements["exported_history"] = True
                    self.notify_achievement("Weather history exported successfully!")
                    self.save_achievements()
                    self.update_achievements_display()

            except Exception as e:
                messagebox.showerror("Export Failed", f"An error occurred: {e}")

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_theme_preference()

    def apply_theme(self):
        t = self.themes[self.current_theme]
        self.root.configure(bg=t["bg"])

        # Apply theme recursively
        def apply_recursive(widget):
            for w in widget.winfo_children():
                if isinstance(w, (tk.Label, tk.Button)):
                    w.configure(bg=t["bg"], fg=t["fg"])
                if isinstance(w, tk.Entry):
                    w.configure(bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["fg"])
                if isinstance(w, tk.Frame):
                    w.configure(bg=t["bg"])
                apply_recursive(w)

        apply_recursive(self.root)

        self.stats_canvas.configure(bg="white" if self.current_theme == "light" else "#3C3F41")
        self.weather_label.configure(bg=t["bg"], fg=t["fg"])
        self.stats_label.configure(bg=t["bg"], fg=t["fg"])

        self.achievements_text.configure(
            bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["fg"]
        )

    def save_theme_preference(self):
        try:
            with open("theme_pref.json", "w") as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            print(f"Error saving theme preference: {e}")

    def load_theme_preference(self):
        try:
            with open("theme_pref.json", "r") as f:
                data = json.load(f)
                self.current_theme = data.get("theme", "light")
        except FileNotFoundError:
            self.current_theme = "light"

    def load_achievements(self):
        try:
            with open(self.ACHIEVEMENTS_FILE, "r") as f:
                data = json.load(f)
                self.achievements = data.get("achievements", self.achievements)
                self.searched_cities = set(data.get("searched_cities", []))
        except FileNotFoundError:
            pass

    def save_achievements(self):
        data = {
            "achievements": self.achievements,
            "searched_cities": list(self.searched_cities)
        }
        try:
            with open(self.ACHIEVEMENTS_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving achievements: {e}")

    def notify_achievement(self, message):
        messagebox.showinfo("Achievement Unlocked!", message)

    def update_achievements_display(self):
        self.achievements_text.configure(state="normal")
        self.achievements_text.delete(1.0, tk.END)

        achv = self.achievements
        used_units = achv["used_both_units"]

        lines = [
            f"First Search: {'✅' if achv['first_search'] else '❌'}",
            f"Five Cities Searched: {'✅' if achv['five_cities'] else '❌'}",
            f"Extreme Temperature Seen: {'✅' if achv['temp_extreme'] else '❌'}",
            f"Weather History Exported: {'✅' if achv['exported_history'] else '❌'}",
            f"Used Imperial Units: {'✅' if used_units['imperial'] else '❌'}",
            f"Used Metric Units: {'✅' if used_units['metric'] else '❌'}",
        ]

        self.achievements_text.insert(tk.END, "\n".join(lines))
        self.achievements_text.configure(state="disabled")

    def run(self):
        self.root.mainloop()

# Run the app
if __name__ == "__main__":
    app = WeatherApp()
    app.run()
