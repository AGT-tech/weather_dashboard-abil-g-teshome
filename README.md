# 🌦️ Weather Dashboard App

A feature-rich desktop GUI application that allows users to fetch, visualize, and analyze weather data by city. Built with Python, Tkinter, and OpenWeatherMap API, the app includes trend detection, achievements, dark/light themes, and CSV integration.

---

## 🚀 Features

- 🔍 **Current Weather**: Search weather by city with support for metric and imperial units.
- 📈 **Trend Detection**: Uses linear regression to determine temperature trends.
- 📊 **Statistics Dashboard**: Displays average, min, and max temperatures.
- 🌈 **Theming**: Switch between light, dark, and custom themes.
- 🏆 **Achievements System**: Unlock milestones as you explore more cities or export data.
- 📂 **CSV Integration**: Load city data from a `.csv` file and export history.
- 🖼️ **Icons & Forecasts**: Includes weather icons and optional 5-day forecasts.
- 💾 **Local Storage**: Weather history is stored using SQLite.

---

## 🖥️ Demo

![App Screenshot](assets/screenshots/dashboard.png) <!-- Replace with an actual screenshot path if available -->

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/weather-dashboard.git
   cd weather-dashboard

2. **Create a virtual environment (optional but recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt

4. **Set up your .env file**
    **Create a .env file in the root directory:**
    ```ini
    WEATHER_API_KEY=your_openweathermap_api_key
    DATABASE_PATH=weather_data.db

## 🧪 Running the App
    python main.py

## 🗃️ Project Structure

```plaintext
weather-dashboard/
├── assets/
│   └── icons/                    # Weather condition icons (e.g. clear.png, rain.png)
├── config.py                     # Configuration loader using environment variables
├── core/
│   ├── api.py                    # WeatherAPI class for fetching weather and forecast
│   ├── processor.py              # DataProcessor for handling API responses
│   └── storage.py                # WeatherDB for SQLite-based history storage
├── data/
│   ├── custom_themes.json        # Optional user-defined themes
│   └── theme_pref.json           # Stores user's theme preference
├── features/
│   ├── achievement_manager.py    # AchievementManager for unlocking badges
│   ├── statistics_manager.py     # StatisticsManager for calculating min/avg/max/trend
│   ├── theme_manager.py          # ThemeManager for switching between themes
│   └── trend_manager.py          # TrendDetector using linear regression
├── group_csv.csv                 # Optional CSV input file for batch city search
├── gui/
│   └── weather_gui.py            # Main GUI class built with Tkinter
├── utils/
│   └── logger_config.py          # Logging configuration setup
├── main.py                       # App entry point
├── .env                          # Environment variables (e.g. API key)
└── requirements.txt              # Python dependencies
```

## 📦 Usage

Using the App

- Enter a city name in the text box.

- Select temperature unit (Imperial or Metric).

- Click “Get Weather” to fetch current data.

- Use “Switch Theme” to toggle between light/dark modes.

- Use “Show Search History” or “Export History” as needed.

- Load multiple cities from CSV via “Load Cities from CSV”.




## 🧩 Requirements

- Python 3.8+
- dependencies: Tkinter, requests, matplotlib, python-dotenv, sqlite3

Installl all with:
pip install -r requirements.txt

## 🌐 API Used

- OpenWeatherMap API

## ✨ Contributions

- Feel free to open issues or submit pull requests!

## 📄 License
MIT License

## 🙋‍♀️ Author

Created by Abil G Teshome | @AGT-tech


