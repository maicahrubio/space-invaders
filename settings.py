import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    """Loads settings from settings.json."""
    if not os.path.exists(SETTINGS_FILE):
        return {"sound_volume": 80, "mobile_controls": False}

    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {"sound_volume": 80, "mobile_controls": False}

def save_settings(settings_dict):
    """Saves settings to settings.json."""
    try:
        with open(SETTINGS_FILE, "w") as file:
            json.dump(settings_dict, file, indent=4)
        print("Settings saved!")
    except Exception as e:
        print(f"Error saving settings: {e}")