from playwright.sync_api import sync_playwright
from automation.config import (
    STATE_PATH,
    HEADLESS,
    SLOW_MO
)


def login_and_save_session():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO
        )

        context = browser.new_context()

        page = context.new_page()

        print("Opening LinkedIn login page...")

        page.goto("https://www.linkedin.com/login")

        input(
            "\nLogin manually and open your LinkedIn feed.\n"
            "When you can see your feed, press ENTER here..."
        )

        print("Saving session...")

        context.storage_state(path=STATE_PATH)

        print(f"Session saved to: {STATE_PATH}")

        browser.close()


if __name__ == "__main__":
    login_and_save_session()