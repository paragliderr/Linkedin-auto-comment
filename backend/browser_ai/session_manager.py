import pickle
import os
from urllib.parse import urlparse
from auto_sel.utils.driver import get_driver

_driver = None
_active_url = None

COOKIE_DIR = os.path.join("user_data", "browser_ai_sessions")


def _domain_key(url: str) -> str:
    netloc = urlparse(url).netloc or url
    return netloc.replace(":", "_").replace("/", "_")


def _cookie_path(url: str) -> str:
    os.makedirs(COOKIE_DIR, exist_ok=True)
    return os.path.join(COOKIE_DIR, f"{_domain_key(url)}.pkl")


def _driver_alive() -> bool:
    global _driver
    if _driver is None:
        return False
    try:
        _ = _driver.current_url
        return True
    except Exception:
        _driver = None
        return False


def start_or_save(url: str):
    """Single entry point behind the 'Open & Save Login Session' button.

    First click (no browser open yet): opens the site, loads a saved
    session if one exists for this domain, or waits for manual login.

    Second click (browser already open from the first click): assumes
    the user has now logged in manually, and saves the current cookies.
    """
    global _driver, _active_url

    if not url:
        raise ValueError("url is required")

    if _driver_alive() and _active_url == url:

        with open(_cookie_path(url), "wb") as f:
            pickle.dump(_driver.get_cookies(), f)
        return {"status": "saved", "logged_in": True}

    if _driver_alive():
        _driver.quit()

    _driver = get_driver()
    _active_url = url
    _driver.get(url)

    cookie_path = _cookie_path(url)
    if os.path.exists(cookie_path):
        with open(cookie_path, "rb") as f:
            for cookie in pickle.load(f):
                try:
                    _driver.add_cookie(cookie)
                except Exception:
                    pass
        _driver.refresh()
        return {"status": "restored_session", "logged_in": True}

    return {"status": "needs_manual_login", "logged_in": False}


def close_session():
    global _driver, _active_url
    if _driver_alive():
        _driver.quit()
    _driver = None
    _active_url = None
    return {"status": "closed"}