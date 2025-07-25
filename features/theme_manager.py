# core/theme_manager.py

import os
import json
import tkinter as tk

class ThemeManager:
    def __init__(self, root):
        self.root = root
        # Theme setup with light/dark options
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

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.save_theme_preference()

    def apply_theme(self):
        theme = self.themes[self.current_theme]
        self.root.configure(bg=theme["bg"])

        def recursive_color_update(widget):
            for child in widget.winfo_children():
                if isinstance(child, (tk.Frame, tk.LabelFrame)):
                    child.configure(bg=theme["bg"])
                elif isinstance(child, tk.Label):
                    child.configure(bg=theme["bg"], fg=theme["fg"])
                elif isinstance(child, tk.Button):
                    child.configure(bg=theme["button_bg"], fg=theme["button_fg"], activebackground=theme["button_bg"])
                elif isinstance(child, tk.Entry):
                    child.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], insertbackground=theme["entry_fg"])
                elif isinstance(child, tk.Listbox):
                    child.configure(bg=theme["entry_bg"], fg=theme["entry_fg"], selectbackground="#6A95FF")
                elif isinstance(child, tk.Canvas):
                    child.configure(bg=theme["bg"])
                recursive_color_update(child)

        recursive_color_update(self.root)

    def load_theme_preference(self):
        try:
            with open("data/theme_pref.json", "r") as f:
                data = json.load(f)
                if data.get("theme") in self.themes:
                    self.current_theme = data["theme"]
        except FileNotFoundError:
            self.current_theme = "light"

    def save_theme_preference(self):
        os.makedirs("data", exist_ok=True)
        with open("data/theme_pref.json", "w") as f:
            json.dump({"theme": self.current_theme}, f)
