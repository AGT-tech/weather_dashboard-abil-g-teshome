import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.api import WeatherAPI
from config import Config
from core.processor import DataProcessor
from datetime import datetime
import os

class WeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("900x600")

        # Load config and create WeatherAPI instance
        config = Config.from_environment()
        self.weather_api = WeatherAPI(api_key=config.api_key)  # timeout=config.request_timeout)

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

        # Weather output frame (rounded style)
        self.weather_frame = tk.Frame(main_frame, bd=2, relief="groove", padx=15, pady=15)
        self.weather_frame.pack(side="left", fill="both", expand=True, padx=(0,10), pady=5)

        self.weather_label = tk.Label(self.weather_frame, text="Weather info will appear here", font=("Helvetica", 14), justify="center")
        self.weather_label.pack(expand=True)

        # Stats with tabs frame
        stats_frame = tk.Frame(main_frame, bd=2, relief="groove")
        stats_frame.pack(side="left", fill="both", expand=True, pady=5)

        self.tab_control = ttk.Notebook(stats_frame)
        self.tab_control.pack(fill="both", expand=True)

        # Tab 1 - Temperature Stats with a canvas for graph
        temp_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(temp_tab, text="Temperature Stats")

        self.stats_label = tk.Label(temp_tab, text="Statistics will appear here", font=("Helvetica", 14), justify="center")
        self.stats_label.pack(pady=10)

        # Canvas placeholder for graph
        self.stats_canvas = tk.Canvas(temp_tab, width=300, height=250, bg="white", bd=1, relief="sunken")
        self.stats_canvas.pack(padx=10, pady=10)

        # Export button at bottom centered
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", pady=10)
        export_btn = tk.Button(bottom_frame, text="Export Weather History to CSV", command=self.export_history)
        export_btn.pack()

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

            # Rounded display of weather info
            weather_text = (
                f"{processed['city']}\n"
                f"{processed['description'].title()}\n"
                f"Temp: {processed['temperature']}{processed['unit']}\n"
                f"Feels Like: {processed['feels_like']}{processed['unit']}\n"
                f"Humidity: {processed['humidity']}%\n"
                f"Wind: {processed['wind_speed']}"
            )
            self.weather_label.config(text=weather_text)

            # Update stats tab as well
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

        # Simple bar graph for temperatures on canvas
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

        # Normalize temps to canvas height
        def norm(temp):
            return height - margin - ((temp - min_temp) / (max_temp - min_temp + 1e-5) * (height - 2*margin))

        for i, temp in enumerate(temps):
            x0 = margin + i * bar_width
            y0 = norm(temp)
            x1 = x0 + bar_width - 2
            y1 = height - margin
            self.stats_canvas.create_rectangle(x0, y0, x1, y1, fill="skyblue")
            self.stats_canvas.create_text(x0 + bar_width/2 - 1, y0 - 10, text=str(temp), font=("Helvetica", 9), anchor="s")

    def export_history(self):
        if not self.weather_history:
            messagebox.showinfo("Export", "No data to export.")
            return

        import os
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
            except Exception as e:
                messagebox.showerror("Export Failed", f"An error occurred: {e}")

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_theme_preference()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])
        self._apply_theme_recursive(self.root, theme)

    def _apply_theme_recursive(self, widget, theme):
        # Safely apply bg/fg only to widgets that support it
        # Use widget.winfo_class() to differentiate widget types
        cls = widget.winfo_class()
        try:
            if cls in ("Frame", "TFrame", "Labelframe"):
                widget.configure(bg=theme["bg"])
            elif cls in ("Label", "TLabel"):
                widget.configure(bg=theme["bg"], fg=theme["fg"])
            elif cls in ("Button", "TButton"):
                widget.configure(bg=theme["button_bg"], fg=theme["button_fg"],
                                 activebackground=theme["bg"], activeforeground=theme["fg"])
            elif cls == "Entry":
                widget.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])
            elif cls == "Canvas":
                widget.configure(bg=theme["bg"])
        except tk.TclError:
            # Some ttk widgets do not support bg config, just skip
            pass

        for child in widget.winfo_children():
            self._apply_theme_recursive(child, theme)

    def save_theme_preference(self):
        try:
            with open("theme_config.txt", "w") as f:
                f.write(self.current_theme)
        except Exception as e:
            print(f"Error saving theme: {e}")

    def load_theme_preference(self):
        try:
            with open("theme_config.txt", "r") as f:
                saved_theme = f.read().strip()
                if saved_theme in self.themes:
                    self.current_theme = saved_theme
        except FileNotFoundError:
            pass  # default to light theme

    def run(self):
        self.root.mainloop()


# Run the app
if __name__ == "__main__":
    app = WeatherApp()
    app.run()
