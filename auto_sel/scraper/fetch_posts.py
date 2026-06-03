import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MIN_CONTENT_LENGTH = 100
ACTION_WORDS = {"Like", "Comment", "Repost", "Send", "React", "Share"}
JUNK_PREFIXES = ["people you may know", "people in your network", "add to your feed",
                 "suggested for you", "promoted", "try premium", "news"]


def _get_post_url(driver, container) -> str:
    return driver.execute_script("""
        var anchors = arguments[0].querySelectorAll('a[href]');
        var best = null;
        for (var i = 0; i < anchors.length; i++) {
            var href = anchors[i].href || '';
            if (!['/posts/', '/feed/update/', '/pulse/'].some(p => href.includes(p))) continue;
            if (href.includes('commentUrn') || href.includes('reactionType')) continue;
            if (!best || href.length < best.length) best = href;
        }
        return best ? best.split('?')[0] : '';
    """, container) or ""


def fetch_posts(driver, target_posts=20, max_scrolls=25):
    driver.get("https://www.linkedin.com/feed/")

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='mainFeed']"))
        )
    except Exception:
        print("Feed load timeout — continuing anyway.")

    time.sleep(3)
    print(f"\nTarget: {target_posts} posts | Max scrolls: {max_scrolls}")

    # Scroll down until we have enough post cards
    stall, last_count = 0, 0
    for i in range(1, max_scrolls + 1):
        count = len(driver.find_elements(By.CSS_SELECTOR, "div[role='listitem'][componentkey]"))
        print(f"  Scroll {i:2d} | containers: {count}")
        if count >= target_posts * 2:
            break
        stall = stall + 1 if count == last_count else 0
        if stall >= 3:
            print("  Feed stopped loading — moving on.")
            break
        last_count = count
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    # Click all see more buttons so we get full post text
    buttons = driver.find_elements(By.CSS_SELECTOR, "[data-testid='expandable-text-button']")
    print(f"\nExpanding {len(buttons)} truncated posts...")
    for btn in buttons:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", btn)
            time.sleep(0.15)
        except Exception:
            pass
    time.sleep(2)

    containers = driver.find_elements(By.CSS_SELECTOR, "div[role='listitem'][componentkey]")
    print(f"Processing {len(containers)} containers...\n")

    posts, seen = [], set()

    for container in containers:
        try:
            box = container.find_elements(By.CSS_SELECTOR, "[data-testid='expandable-text-box']")
            if not box:
                continue

            content = "\n".join(
                l for l in box[0].text.splitlines() if l.strip() not in ACTION_WORDS
            ).strip()

            if len(content) < MIN_CONTENT_LENGTH:
                continue
            if any(content.splitlines()[0].lower().startswith(j) for j in JUNK_PREFIXES):
                continue
            if content[:200] in seen:
                continue

            seen.add(content[:200])
            posts.append({"post_url": _get_post_url(driver, container), "content": content})

            if len(posts) >= target_posts:
                break
        except Exception as e:
            print(f"  Skipped: {e}")

    with_url = sum(1 for p in posts if p["post_url"])
    print(f"Collected {len(posts)} posts | {with_url} with URL | {len(posts) - with_url} missing URL")
    return posts