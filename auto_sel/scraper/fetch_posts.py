import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── Patterns that make a URL a real post link (not a profile/company page) ─
POST_URL_PATTERNS = re.compile(
    r"linkedin\.com/(posts/|feed/update/|pulse/)"
)

# Text that indicates a container is a sidebar widget, not a feed post
JUNK_TEXT_PREFIXES = [
    "people you may know",
    "people in your network",
    "add to your feed",
    "suggested for you",
    "promoted",
    "try premium",
    "news",
]

ACTION_WORDS = {"Like", "Comment", "Repost", "Send", "React", "Share"}

MIN_CONTENT_LENGTH = 100


def _get_post_url(driver, container) -> str:
    """
    Inside a post container, find an <a> whose href matches a real post URL
    (/posts/, /feed/update/, /pulse/).  The timestamp anchor is the most
    reliable one — it always points to the canonical post URL.
    Returns empty string if none found.
    """
    url = driver.execute_script("""
        var container = arguments[0];
        var anchors = container.querySelectorAll('a[href]');
        var patterns = ['/posts/', '/feed/update/', '/pulse/'];
        // Prefer the shortest matching href — timestamp links are concise;
        // reaction/comment deep-links are long and contain extra segments.
        var best = null;
        for (var i = 0; i < anchors.length; i++) {
            var href = anchors[i].href || '';
            // Must match a post pattern
            var matches = patterns.some(function(p){ return href.indexOf(p) !== -1; });
            if (!matches) continue;
            // Must NOT be a comment/reaction deep-link
            if (href.indexOf('commentUrn') !== -1) continue;
            if (href.indexOf('reactionType') !== -1) continue;
            if (best === null || href.length < best.length) best = href;
        }
        return best ? best.split('?')[0] : '';
    """, container)
    return url or ""


def _clean_content(text: str) -> str:
    """Strip action-bar words that Selenium picks up as part of the text."""
    lines = [l for l in text.splitlines() if l.strip() not in ACTION_WORDS]
    return "\n".join(lines).strip()


def fetch_posts(driver, target_posts: int = 20, max_scrolls: int = 25) -> list[dict]:
    """
    Scrape LinkedIn feed posts.

    Container anchor: div[role=listitem][componentkey]
    Each such div is one feed card.  We scope all selectors inside it so
    sidebar widgets, ads, and "People you may know" cards are never mixed in.
    """

    driver.get("https://www.linkedin.com/feed/")

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-testid='mainFeed']")
            )
        )
    except Exception:
        print("Feed load timeout — continuing anyway.")

    time.sleep(3)
    print(f"\nTarget: {target_posts} posts | Max scrolls: {max_scrolls}")

    # ── Scroll until enough listitem containers are present ────────────────
    stall = 0
    last_count = 0

    for scroll_num in range(1, max_scrolls + 1):
        containers = driver.find_elements(
            By.CSS_SELECTOR,
            "div[role='listitem'][componentkey]"
        )
        count = len(containers)
        print(f"  Scroll {scroll_num:2d} | listitem containers: {count}")

        if count >= target_posts * 2:
            break

        if count == last_count:
            stall += 1
            if stall >= 3:
                print("  No new posts loading — stopping scroll.")
                break
        else:
            stall = 0
        last_count = count

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    # ── Expand truncated posts ─────────────────────────────────────────────
    print("\nExpanding truncated posts...")
    more_buttons = driver.find_elements(
        By.CSS_SELECTOR, "[data-testid='expandable-text-button']"
    )
    print(f"  Found {len(more_buttons)} expand buttons")
    for btn in more_buttons:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(0.15)
        except Exception:
            pass
    time.sleep(2)

    # ── Extract content + URL from each container ──────────────────────────
    containers = driver.find_elements(
        By.CSS_SELECTOR,
        "div[role='listitem'][componentkey]"
    )
    print(f"\nProcessing {len(containers)} containers...")

    posts = []
    seen = set()

    for container in containers:
        try:
            # 1. Find the text box scoped inside this container only
            text_boxes = container.find_elements(
                By.CSS_SELECTOR, "[data-testid='expandable-text-box']"
            )
            if not text_boxes:
                continue

            content = _clean_content(text_boxes[0].text)

            # 2. Length gate
            if len(content) < MIN_CONTENT_LENGTH:
                continue

            # 3. Junk text gate
            first_line = content.splitlines()[0].lower() if content else ""
            if any(first_line.startswith(j) for j in JUNK_TEXT_PREFIXES):
                continue

            # 4. Dedup
            key = content[:200]
            if key in seen:
                continue
            seen.add(key)

            # 5. Get URL — scoped to this container
            url = _get_post_url(driver, container)

            posts.append({"post_url": url, "content": content})

            if len(posts) >= target_posts:
                break

        except Exception as e:
            print(f"  ⚠  Skipped container: {e}")
            continue

    with_url = sum(1 for p in posts if p["post_url"])
    print(f"\nCollected {len(posts)} posts | {with_url} with URL | {len(posts)-with_url} missing URL")
    return posts