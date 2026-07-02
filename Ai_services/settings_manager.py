import json
from pathlib import Path

from Ai_services.config import (
    CHATBOT_API_KEY,
    BASE_URL,
    MODEL_NAME,
)

SETTINGS_PATH = (
    Path(__file__).resolve().parent.parent
    / "settings.json"
)


DEFAULT_SETTINGS = {
    "api_key": "",
    "base_url": "",
    "model": ""
}


def get_ai_settings():

    if not SETTINGS_PATH.exists():

        with open(SETTINGS_PATH, "w") as file:
            json.dump(DEFAULT_SETTINGS, file, indent=4)

    with open(SETTINGS_PATH, "r") as file:
        settings = json.load(file)

    return {
        "api_key": settings.get("api_key") or CHATBOT_API_KEY,
        "base_url": settings.get("base_url") or BASE_URL,
        "model": settings.get("model") or MODEL_NAME,
    }