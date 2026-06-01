from playwright.sync_api import sync_playwright
from automation.config import FEED_URL, STATE_PATH

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        storage_state=STATE_PATH
    )

    page = context.new_page()

    page.goto(FEED_URL)

    page.wait_for_timeout(8000)

    menus = page.locator(
        "button[aria-label*='Open control menu for post by']"
    )

    print("Posts found:", menus.count())

    for i in range(min(menus.count(), 5)):

        print("\n" + "=" * 60)
        print(f"POST {i+1}")
        print("=" * 60)

        menu = menus.nth(i)

        post = menu.locator("xpath=../..")

        text = post.inner_text()

        print(text[:1000])

    input("\nPress Enter to close...")