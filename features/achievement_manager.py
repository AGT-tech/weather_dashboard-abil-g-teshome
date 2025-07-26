import os
import json
from tkinter import messagebox

class AchievementManager:
    def __init__(self, listbox_widget, searched_cities):
        """
        Initialize the AchievementManager.

        Args:
            listbox_widget: Tkinter Listbox widget used to display achievements.
            searched_cities: A set to track the cities that have been searched.
        """
        self.listbox_widget = listbox_widget
        self.searched_cities = searched_cities

        # Achievement flags to track progress
        self.achievements = {
            "first_search": False,
            "five_cities": False,
            "temp_extreme": False,
            "exported_history": False,
            "used_both_units": {"imperial": False, "metric": False}
        }

        # Human-readable descriptions for each achievement
        self.achievement_texts = {
            "first_search": "First Search Completed",
            "five_cities": "Searched 5 Different Cities",
            "temp_extreme": "Encountered Temperature Extremes",
            "exported_history": "Exported Search History",
            "used_both_units": "Used Both Imperial and Metric Units"
        }

        self.load_achievements()
        self.update_display()

    def check_achievements(self, data, city, units):
        """
        Check and unlock achievements based on weather data and user actions.

        Args:
            data (dict): Processed weather data containing temperature.
            city (str): The city just searched.
            units (str): The units used for the request ('imperial' or 'metric').
        """
        unlocked_new = False

        # First search achievement
        if not self.achievements["first_search"]:
            self.achievements["first_search"] = True
            unlocked_new = True

        # Track unique cities searched
        self.searched_cities.add(city.lower())
        if not self.achievements["five_cities"] and len(self.searched_cities) >= 5:
            self.achievements["five_cities"] = True
            unlocked_new = True

        # Extreme temperature achievement
        temp = data["temperature"]
        if units == "imperial":
            if not self.achievements["temp_extreme"] and (temp < 0 or temp > 100):
                self.achievements["temp_extreme"] = True
                unlocked_new = True
        else:  # metric
            if not self.achievements["temp_extreme"] and (temp < -17.8 or temp > 37.8):
                self.achievements["temp_extreme"] = True
                unlocked_new = True

        # Track unit usage
        self.achievements["used_both_units"][units] = True

        # Save and notify if anything unlocked
        if unlocked_new:
            self.save_achievements()
            self.update_display()
            messagebox.showinfo("Achievement Unlocked!", "You unlocked a new achievement!")

    def export_achievement(self):
        """
        Mark the export history achievement as completed.
        """
        if not self.achievements["exported_history"]:
            self.achievements["exported_history"] = True
            self.save_achievements()
            self.update_display()
            messagebox.showinfo("Achievement Unlocked!", "Exported your search history!")

    def update_display(self):
        """
        Refresh the achievements listbox with currently unlocked achievements.
        """
        self.listbox_widget.delete(0, "end")
        for key, unlocked in self.achievements.items():
            if key == "used_both_units":
                if unlocked["imperial"] and unlocked["metric"]:
                    self.listbox_widget.insert("end", self.achievement_texts[key])
            elif unlocked:
                self.listbox_widget.insert("end", self.achievement_texts[key])

    def save_achievements(self):
        """
        Persist the current achievements to a JSON file.
        """
        os.makedirs("data", exist_ok=True)
        with open("data/achievements.json", "w") as f:
            json.dump(self.achievements, f)

    def load_achievements(self):
        """
        Load achievement data from file if available.
        """
        try:
            with open("data/achievements.json", "r") as f:
                saved = json.load(f)
                for key in self.achievements:
                    if key in saved:
                        self.achievements[key] = saved[key]
        except FileNotFoundError:
            pass
