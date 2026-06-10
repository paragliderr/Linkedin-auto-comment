from playwright.sync_api import sync_playwright

from automation.config import (
    FEED_URL,
    STATE_PATH
)

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context(
        storage_state=STATE_PATH,
        permissions=[
            "clipboard-read",
            "clipboard-write"
        ]
    )

    page = context.new_page()

    page.goto(FEED_URL)

    page.wait_for_timeout(8000)

    menus = page.locator(
        "button[aria-label*='Open control menu for post by']"
    )

    count = min(
        menus.count(),
        3
    )

    print(
        f"Found {menus.count()} posts"
    )

    for i in range(count):

        print("\n" + "=" * 60)
        print(f"POST {i+1}")
        print("=" * 60)

        menu = menus.nth(i)

        menu.click()

        page.wait_for_timeout(2000)

        page.get_by_text(
            "Copy link to post"
        ).click()

        page.wait_for_timeout(3000)

        url = page.evaluate(
            "() => navigator.clipboard.readText()"
        )

        print(url)

        page.keyboard.press("Escape")

        page.wait_for_timeout(1000)

    input(
        "\nPress Enter to close..."
    )

    browser.close()