from pathlib import Path
import sys


if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).resolve().parent.parent


USER_DATA_DIR = APP_DIR / "user_data"
USER_DATA_DIR.mkdir(exist_ok=True)


SETTINGS_PATH = USER_DATA_DIR / "settings.json"

COOKIES_PATH = USER_DATA_DIR / "cookies.pkl"

STATE_PATH = USER_DATA_DIR / "state.json"

POSTS_CSV_PATH = USER_DATA_DIR / "linkedin_posts.csv"