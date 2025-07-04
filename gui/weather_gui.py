import tkinter as tk

class WeatherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Weather Dashboard")
        self.root.geometry("400x300")

    def run(self):
        self.root.mainloop()

# Run the app
if __name__ == "__main__":
    app = WeatherApp()
    app.run()