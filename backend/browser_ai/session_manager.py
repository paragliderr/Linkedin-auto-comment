import pickle
import os
from auto_sel.utils.driver import get_driver
from backend.browser_ai.adapters import ChatSiteAdapter

_driver = None
_adapter = None

COOKIE_PATH = os.path.join("user_data", "browserai_cookies.pkl")


def start_session(url: str, input_css: str, send_css: str, reply_css: str):
    global _driver, _adapter

    if _driver is not None:
        try:
            _ = _driver.current_url
            return {"status": "already_running"}
        except Exception:
            _driver = None

    os.makedirs("user_data", exist_ok=True)

    _adapter = ChatSiteAdapter(url, input_css, send_css, reply_css)
    _driver = get_driver()
    _driver.get(url)

    if os.path.exists(COOKIE_PATH):
        with open(COOKIE_PATH, "rb") as f:
            for cookie in pickle.load(f):
                try:
                    _driver.add_cookie(cookie)
                except Exception:
                    pass
        _driver.refresh()
        return {"status": "restored_session"}

    return {"status": "needs_manual_login", "message": "Log in in the opened window, then call /save-session"}


def save_session():
    if _driver is None:
        return {"status": "no_active_session"}
    os.makedirs("user_data", exist_ok=True)
    with open(COOKIE_PATH, "wb") as f:
        pickle.dump(_driver.get_cookies(), f)
    return {"status": "saved"}


def send_message(message: str) -> str:
    if _driver is None or _adapter is None:
        raise RuntimeError("No active browser-chat session — call /start first")
    return _adapter.send_message(_driver, message)


def close_session():
    global _driver, _adapter
    if _driver is not None:
        _driver.quit()
    _driver = None
    _adapter = None
    return {"status": "closed"}


def check_session():
    return {"exists": os.path.exists(COOKIE_PATH)}