import sqlite3
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import csv

# ──────────────────────────────
# Logger Setup with Rotation
# ──────────────────────────────

logger = logging.getLogger("features.weather_db")

if not logger.handlers:
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Rotating file handler: max 1MB per file, keep 5 backups
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Default log level
    logger.setLevel(logging.INFO)
    logger.propagate = False


class WeatherDB:
    """
    SQLite database manager for the weather app.

    Responsibilities:
    - Store weather history entries with detailed weather data.
    - Manage user preferences as key-value pairs.
    - Track user achievements similarly as key-value pairs.
    - Export weather history to CSV.
    - Log operations with rotating log files and optional debug mode.
    """

    def __init__(self, db_path="data/weather_app.db", debug=False, prefs=None):
        """
        Initialize the WeatherDB instance.

        Creates the database and tables if they don't exist. Sets logging level
        based on debug flag or preferences.

        Args:
            db_path (str): Path to SQLite database file.
            debug (bool): Enables DEBUG-level logging if True.
            prefs (dict or None): Optional preferences dictionary; enables debug mode if
                                  prefs.get("debug_mode") == "true".
        """
        # Determine debug mode from argument or preferences
        debug_mode = debug or (prefs and prefs.get("debug_mode") == "true")
        if debug_mode:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled for WeatherDB.")

        logger.info(f"Initializing WeatherDB at '{db_path}'")
        # Ensure directory exists for DB file
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        # Connect to SQLite database
        self.conn = sqlite3.connect(db_path)
        # Create required tables if missing
        self.create_tables()

    def create_tables(self):
        """
        Create required tables if they do not exist:
        - weather_history: stores weather entries
        - preferences: stores key-value user preferences
        - achievements: stores user achievements

        Commits changes after creation.
        """
        logger.debug("Creating tables if missing...")
        c = self.conn.cursor()

        # Table for storing weather history records
        c.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                temperature INTEGER,
                feels_like INTEGER,
                humidity INTEGER,
                description TEXT,
                wind_speed TEXT,
                unit TEXT,
                timestamp TEXT
            )
        ''')

        # Table for user preferences
        c.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # Table for achievements tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                name TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        self.conn.commit()
        logger.debug("Tables created or already exist.")

    def save_weather_entry(self, entry: dict):
        """
        Save a new weather entry into the weather_history table.

        Extracts expected fields from the entry dictionary and adds a timestamp.

        Args:
            entry (dict): Dictionary with keys:
                'city', 'temperature', 'feels_like', 'humidity',
                'description', 'wind_speed', 'unit'.

        Side effects:
            Commits the new entry to the database.
            Logs the save operation.
        """
        logger.debug(f"Saving weather entry: {entry}")
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO weather_history (
                city, temperature, feels_like, humidity,
                description, wind_speed, unit, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.get('city'),
            entry.get('temperature'),
            entry.get('feels_like'),
            entry.get('humidity'),
            entry.get('description'),
            entry.get('wind_speed'),
            entry.get('unit'),
            datetime.now().isoformat()
        ))
        self.conn.commit()
        logger.info("Weather entry saved.")

    def get_weather_history(self) -> list[dict]:
        """
        Retrieve all weather history records in chronological order.

        Returns:
            List of dictionaries, each containing:
            'city', 'temperature', 'feels_like', 'humidity',
            'description', 'wind_speed', 'unit', 'timestamp'.

        Logs the number of records retrieved.
        """
        logger.debug("Fetching weather history...")
        c = self.conn.cursor()
        c.execute('''
            SELECT city, temperature, feels_like, humidity,
                   description, wind_speed, unit, timestamp
            FROM weather_history ORDER BY id
        ''')
        rows = c.fetchall()
        history = [dict(zip(
            ['city', 'temperature', 'feels_like', 'humidity',
             'description', 'wind_speed', 'unit', 'timestamp'], row))
            for row in rows
        ]
        logger.debug(f"Retrieved {len(history)} weather history records.")
        return history

    def save_preference(self, key: str, value: str):
        """
        Save or update a user preference key-value pair.

        Args:
            key (str): Preference key.
            value (str): Preference value.

        Side effects:
            Commits changes to the preferences table.
            Logs the save operation.
        """
        logger.debug(f"Saving preference: {key} = {value}")
        c = self.conn.cursor()
        c.execute('REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()
        logger.info(f"Preference saved: {key}")

    def load_preference(self, key: str):
        """
        Load a single user preference by key.

        Args:
            key (str): Preference key to load.

        Returns:
            str or None: The preference value if found; otherwise None.

        Logs the loaded value.
        """
        logger.debug(f"Loading preference for key: {key}")
        c = self.conn.cursor()
        c.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        row = c.fetchone()
        value = row[0] if row else None
        logger.debug(f"Loaded preference: {key} = {value}")
        return value

    def load_preferences(self) -> dict[str, str]:
        """
        Load all user preferences as a dictionary.

        Returns:
            Dictionary mapping preference keys to their string values.

        Logs all loaded preferences.
        """
        logger.debug("Loading all preferences...")
        c = self.conn.cursor()
        c.execute('SELECT key, value FROM preferences')
        rows = c.fetchall()
        prefs = {key: value for key, value in rows}
        logger.debug(f"Loaded preferences: {prefs}")
        return prefs

    def save_achievement(self, name: str, value: str):
        """
        Save or update an achievement entry.

        Args:
            name (str): Achievement name.
            value (str): Achievement value or status.

        Side effects:
            Commits changes to the achievements table.
            Logs the save operation.
        """
        logger.debug(f"Saving achievement: {name} = {value}")
        c = self.conn.cursor()
        c.execute('REPLACE INTO achievements (name, value) VALUES (?, ?)', (name, value))
        self.conn.commit()
        logger.info(f"Achievement saved: {name}")

    def load_achievements(self) -> dict[str, str]:
        """
        Load all achievements as a dictionary.

        Returns:
            Dictionary mapping achievement names to their values/statuses.

        Logs all loaded achievements.
        """
        logger.debug("Loading achievements...")
        c = self.conn.cursor()
        c.execute('SELECT name, value FROM achievements')
        rows = c.fetchall()
        achievements = {name: value for name, value in rows}
        logger.debug(f"Loaded achievements: {achievements}")
        return achievements

    def export_to_csv(self, file_path: str):
        """
        Export all weather history data to a CSV file.

        Args:
            file_path (str): Destination path for the CSV file.

        Behavior:
            Retrieves all weather history records.
            Writes the data to the CSV file with headers matching record keys.
            If no records exist, logs a warning and does not create the file.
            Catches and logs exceptions during file writing.

        Side effects:
            Creates or overwrites the CSV file at the specified path.
            Logs export success or failure.
        """
        logger.info(f"Exporting weather history to CSV: {file_path}")
        history = self.get_weather_history()
        if not history:
            logger.warning("No weather history to export.")
            return

        keys = history[0].keys()
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(history)
            logger.info(f"Exported {len(history)} records to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")

    def close(self):
        """
        Close the database connection.

        Should be called when the WeatherDB instance is no longer needed to
        free up resources and ensure proper closure.

        Logs the closing event.
        """
        logger.debug("Closing WeatherDB connection.")
        self.conn.close()
        logger.info("Database connection closed.")
