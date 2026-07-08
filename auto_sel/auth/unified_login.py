import os
import pickle
import time
from playwright.sync_api import sync_playwright
from utils.playwright_paths import configure_playwright
from auto_sel.utils.driver import get_driver
from utils.app_paths import COOKIES_PATH, STATE_PATH


LOGIN_TIMEOUT = 300  # seconds

from selenium.common.exceptions import WebDriverException

def wait_for_login(driver, timeout=LOGIN_TIMEOUT):
    """Poll the browser URL instead of blocking on stdin — this must be
    non-interactive since the script is launched headless from the backend.
    Guards against Safari's current_url intermittently returning None,
    and against the user closing the browser window mid-wait."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            url = driver.current_url
        except WebDriverException:
            print("✗ Browser window was closed before login completed.")
            return False

        if url and "linkedin.com/feed" in url:
            return True

        time.sleep(1.5)
    return False

def unified_login():
    print("=" * 60)
    print("LINKEDIN UNIFIED LOGIN")
    print("=" * 60)

    print("\n[1/2] Opening browser for LinkedIn login (Selenium)...")
    driver = get_driver()
    try:
        driver.get("https://www.linkedin.com/login")
        print("Waiting for login in the opened browser window...")

        if not wait_for_login(driver):
            print("✗ Login timed out — no feed detected within 5 minutes.")
            return

        with open(COOKIES_PATH, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        print("✓ Selenium cookies saved")

        print("\n[2/2] Saving Playwright session...")
        cookies = driver.get_cookies()
    finally:
        driver.quit()

    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    
    configure_playwright()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.linkedin.com")

        for cookie in cookies:
            try:
                pw_cookie = {
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": cookie.get("domain", ".linkedin.com"),
                    "path": cookie.get("path", "/"),
                    "httpOnly": cookie.get("httpOnly", False),
                    "secure": cookie.get("secure", False),
                }
                context.add_cookies([pw_cookie])
            except Exception as e:
                print(f"  Skipped cookie: {e}")

        page.goto("https://www.linkedin.com/feed/")
        page.wait_for_timeout(3000)
        context.storage_state(path=STATE_PATH)
        browser.close()

    print("✓ Playwright state saved")
    print("Login complete! Both scrapers are ready to use.")


if __name__ == "__main__":
    unified_login()