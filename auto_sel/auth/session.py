import pickle
import os
from auto_sel.utils.driver import get_driver
from utils.app_paths import COOKIES_PATH


def load_session():
    driver = get_driver()
    driver.get("https://www.linkedin.com")
    
    
    with open(COOKIES_PATH, "rb") as file:
        cookies = pickle.load(file)

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"Skipped cookie: {e}")

    driver.get("https://www.linkedin.com/feed/")  
    return driver

