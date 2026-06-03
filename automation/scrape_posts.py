from playwright.sync_api import sync_playwright

from automation.config import (
    FEED_URL,
    STATE_PATH,
    MAX_POSTS
)

from automation.save_data import save_posts


def scrape_posts(max_posts=MAX_POSTS):

    posts = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            storage_state=STATE_PATH
        )

        page = context.new_page()

        page.goto(FEED_URL)

        page.wait_for_timeout(8000)

        menus = page.locator(
            "button[aria-label*='Open control menu for post by']"
        )

        count = min(
            menus.count(),
            max_posts
        )

        print(f"Found {count} posts")

        for i in range(count):

            try:

                menu = menus.nth(i)

                post = menu.locator(
                    "xpath=../.."
                )

                text = post.inner_text()

                posts.append({
                    "content": text,
                    "post_url": "",
                    "status": "scraped"
                })

                print(
                    f"Scraped post {i+1}"
                )

            except Exception as e:

                print(
                    f"Error on post {i+1}: {e}"
                )

        browser.close()

    return posts


if __name__ == "__main__":

    posts = scrape_posts()
    
    save_posts(posts)

    print()

    for i, post in enumerate(posts):

        print("=" * 60)
        print(f"POST {i+1}")
        print("=" * 60)

        print(
            post["post_text"][:500]
        )