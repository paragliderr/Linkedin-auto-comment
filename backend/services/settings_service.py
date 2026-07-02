import json
from pathlib import Path

SETTINGS_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "settings.json"
)

DEFAULT_SETTINGS = {
    "api_key": "",
    "base_url": "",
    "model": ""
}


def get_settings():
    """
    Returns the current application settings.
    Creates settings.json if it doesn't exist.
    """

    if not SETTINGS_PATH.exists():
        save_settings(DEFAULT_SETTINGS)

    with open(SETTINGS_PATH, "r") as file:
        return json.load(file)


def save_settings(settings: dict):
    """
    Saves the application settings.
    Creates settings.json if needed.
    """

    with open(SETTINGS_PATH, "w") as file:
        json.dump(settings, file, indent=4)

    return True