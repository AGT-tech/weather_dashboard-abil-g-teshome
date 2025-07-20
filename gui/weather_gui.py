import tkinter as tk
import os
from datetime import datetime
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

        #Export to csv
        export_btn = tk.Button(self.root, text="Export to CSV", command=self.export_history)
        export_btn.pack(pady=5)

        # Theme switcher button
        theme_btn = tk.Button(self.root, text="Switch Theme", command=self.toggle_theme)
        theme_btn.pack(pady=5)

        # Apply the current theme to all widgets
        self.apply_theme()


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

            self.weather_history.append(processed)  # Track history for stats

            self.result_label.config(text=(
                f"{processed['city']}:\n"
                f"{processed['description'].title()}\n"
                f"Temp: {processed['temperature']}{processed['unit']}\n"
                f"Feels Like: {processed['feels_like']}{processed['unit']}\n"
                f"Humidity: {processed['humidity']}%\n"
                f"Wind: {processed['wind_speed']}"
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
    
    #Export history function
    def export_history(self):
        if not self.weather_history:
            messagebox.showinfo("Export", "No data to export.")
            return
        
        from tkinter import filedialog
        os.makedirs("data", exist_ok=True)
        file_path = filedialog.asksaveasfilename(
            initialdir=os.path.abspath"data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Weather History"
        )

        if file_path:
            try:
                self.processor.export_to_csv(self.weather_history, file_path)
                messagebox.showinfo("Export Successful", f"Weather history saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"An error occurred: {e}")
    
    # Theme switcher function
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_theme_preference()

    # Apply theme function
    def apply_theme(self):
        theme = self.themes[self.current_theme]

        # Root window
        self.root.configure(bg=theme["bg"])

        # Change all relevant widgets
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            elif isinstance(widget, tk.Entry):
                widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["bg"],activeforeground=theme["fg"])

    def save_theme_preference(self):
        os.makedirs("data", exist_ok=True)
        try:
            with open("data/theme_config.txt", "w") as f:
                f.write(self.current_theme)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def load_theme_preference(self):
        try:
            with open("data/theme_config.txt", "r") as f:
                saved_theme = f.read().strip()
                if saved_theme in self.themes:
                    self.current_theme = saved_theme
        except FileNotFoundError:
            pass # Default to light theme


    def run(self):
        self.root.mainloop()


# Run the app
if __name__ == "__main__":
    app = WeatherApp()
    app.run()


