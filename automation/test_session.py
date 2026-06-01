from playwright.sync_api import sync_playwright
from automation.config import FEED_URL, STATE_PATH


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        storage_state=STATE_PATH
    )

    page = context.new_page()

    page.goto(FEED_URL)

    print("Current URL:", page.url)
    print("Page Title:", page.title())

    input("Press Enter to close...")

    browser.close()