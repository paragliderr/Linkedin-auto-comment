import os
import pickle
from playwright.sync_api import sync_playwright
from auto_sel.utils.driver import get_driver

COOKIE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.pkl")
STATE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "automation", "auth", "state.json")

def unified_login():
    print("=" * 60)
    print("LINKEDIN UNIFIED LOGIN")
    print("=" * 60)

    print("\n[1/2] Opening browser for LinkedIn login (Selenium)...")
    driver = get_driver()
    try:
        driver.get("https://www.linkedin.com/login")
        input("\nLog in to LinkedIn in the browser window.\nOnce you're on the feed, press Enter here...")
        
        with open(COOKIE_PATH, "wb") as f:
            pickle.dump(driver.get_cookies(), f)
        print("✓ Selenium cookies saved")

        print("\n[2/2] Saving Playwright session...")
        cookies = driver.get_cookies()
    finally:
        driver.quit()

    # Convert Selenium cookies to Playwright format 
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.linkedin.com")

        # Add cookies from Selenium session
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
    print("\n Login complete! Both scrapers are ready to use.")


if __name__ == "__main__":
    unified_login()