import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from core.api import WeatherAPI
from config import Config
from core.processor import DataProcessor
from datetime import datetime
import os

class WeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("900x500")

        # Load config and create WeatherAPI instance
        config = Config.from_environment()
        self.weather_api = WeatherAPI(api_key=config.api_key)

        # Instantiate processor and history list
        self.processor = DataProcessor()
        self.weather_history = []

        # Theme handling (simplified here)
        self.current_theme = "light"
        self.themes = {
            "light": {"bg": "#FFFFFF", "fg": "#000000", "button_bg": "#E0E0E0"},
            "dark": {"bg": "#2E2E2E", "fg": "#FFFFFF", "button_bg": "#555555"},
        }

        self.load_theme_preference()

        # Setup UI with frames and tabs
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        # Main content frame: 3 columns
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Left controls
        self.controls_frame = tk.Frame(self.content_frame)
        self.controls_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        tk.Label(self.controls_frame, text="Enter City Name:", font=("Helvetica", 12)).pack(pady=5)
        self.city_entry = tk.Entry(self.controls_frame, font=("Helvetica", 12))
        self.city_entry.pack(pady=5)

        self.unit_var = tk.StringVar(value="imperial")
        unit_dropdown = tk.OptionMenu(self.controls_frame, self.unit_var, "imperial", "metric")
        unit_dropdown.pack(pady=5)

        tk.Button(self.controls_frame, text="Get Weather", command=self.handle_weather_request).pack(pady=10)

        # Center output frame
        self.output_frame = tk.Frame(self.content_frame)
        self.output_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.result_label = tk.Label(self.output_frame, text="", font=("Helvetica", 12), wraplength=300, justify="left")
        self.result_label.pack(pady=10)

        # Right stats frame
        self.stats_frame = tk.Frame(self.content_frame)
        self.stats_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        tk.Button(self.stats_frame, text="Show Stats", command=self.show_statistics).pack(pady=5)

        # Placeholder for charts or detailed stats
        self.chart_container = tk.Frame(self.stats_frame, relief="sunken", bd=1, width=250, height=300)
        self.chart_container.pack(pady=10, fill="both", expand=True)

        # Make columns expandable
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=2)
        self.content_frame.grid_columnconfigure(2, weight=2)

        # Bottom notebook tabs for extras
        self.tab_notebook = ttk.Notebook(self.root)
        self.tab_notebook.pack(fill="x", padx=10, pady=(0,10))

        self.export_tab = tk.Frame(self.tab_notebook)
        self.settings_tab = tk.Frame(self.tab_notebook)

        self.tab_notebook.add(self.export_tab, text="Export")
        self.tab_notebook.add(self.settings_tab, text="Settings")

        # Export tab content
        export_btn = tk.Button(self.export_tab, text="Export Weather History to CSV", command=self.export_history)
        export_btn.pack(pady=20, padx=20)

        # Settings tab content
        theme_btn = tk.Button(self.settings_tab, text="Switch Theme", command=self.toggle_theme)
        theme_btn.pack(pady=20, padx=20)

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
            except Exception as e:
                messagebox.showerror("Export Failed", f"An error occurred: {e}")

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_theme_preference()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])

        for widget in self.root.winfo_children():
            self._apply_widget_theme(widget, theme)

    def _apply_widget_theme(self, widget, theme):
        # Recursive theme application to all children widgets
        if isinstance(widget, tk.Frame) or isinstance(widget, ttk.Frame):
            widget.configure(bg=theme["bg"])
        elif isinstance(widget, tk.Label):
            widget.configure(bg=theme["bg"], fg=theme["fg"])
        elif isinstance(widget, tk.Button):
            widget.configure(bg=theme["button_bg"], fg=theme["fg"], activebackground=theme["bg"], activeforeground=theme["fg"])
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=theme["bg"], fg=theme["fg"], insertbackground=theme["fg"])
        elif isinstance(widget, tk.OptionMenu):
            widget.configure(bg=theme["button_bg"], fg=theme["fg"], activebackground=theme["bg"], activeforeground=theme["fg"])

        # Recursively apply to children widgets
        for child in widget.winfo_children():
            self._apply_widget_theme(child, theme)

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
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = WeatherApp()
    app.run()
