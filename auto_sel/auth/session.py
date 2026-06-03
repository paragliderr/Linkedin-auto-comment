import pickle
import os
from auto_sel.utils.driver import get_driver


def load_session():

    driver = get_driver()

    driver.get("https://www.linkedin.com")
    cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.pkl")
    with open(cookie_path, "rb") as file:
        cookies = pickle.load(file)

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Skipped cookie: {e}")

    driver.refresh()

    return driver


