import sqlite3
import os
from datetime import datetime
import csv


class WeatherDB:
    """Handles SQLite DB operations for the weather app"""

    def __init__(self, db_path="data/weather_app.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
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
        c.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                name TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        self.conn.commit()

    def save_weather_entry(self, entry: dict):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO weather_history (city, temperature, feels_like, humidity, description, wind_speed, unit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

    def get_weather_history(self) -> list[dict]:
        c = self.conn.cursor()
        c.execute('SELECT city, temperature, feels_like, humidity, description, wind_speed, unit, timestamp FROM weather_history ORDER BY id')
        rows = c.fetchall()
        return [dict(zip(['city', 'temperature', 'feels_like', 'humidity', 'description', 'wind_speed', 'unit', 'timestamp'], row)) for row in rows]

    def save_preference(self, key: str, value: str):
        c = self.conn.cursor()
        c.execute('REPLACE INTO preferences (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()

    def load_preference(self, key: str):
        c = self.conn.cursor()
        c.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        row = c.fetchone()
        return row[0] if row else None

    def load_preferences(self) -> dict[str, str]:
        c = self.conn.cursor()
        c.execute('SELECT key, value FROM preferences')
        rows = c.fetchall()
        return {key: value for key, value in rows}

    def save_achievement(self, name: str, value: str):
        c = self.conn.cursor()
        c.execute('REPLACE INTO achievements (name, value) VALUES (?, ?)', (name, value))
        self.conn.commit()

    def load_achievements(self) -> dict[str, str]:
        c = self.conn.cursor()
        c.execute('SELECT name, value FROM achievements')
        rows = c.fetchall()
        return {name: value for name, value in rows}

    def export_to_csv(self, file_path: str):
        history = self.get_weather_history()
        if not history:
            return
        keys = history[0].keys()
        with open(file_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(history)

    def close(self):
        self.conn.close()
