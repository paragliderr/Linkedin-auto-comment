import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def _type_into_editor(driver, box, text):
    driver.execute_script("arguments[0].focus();", box)
    time.sleep(0.2)
    driver.execute_script("arguments[0].innerText = arguments[1];", box, text)
    time.sleep(0.3)
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", box
    )
    time.sleep(1.5)


def _find_comment_button(driver, timeout=10):
    """Locate the post-level 'Comment' action button. Matches loosely
    against visible text OR aria-label, since LinkedIn's markup can attach
    the label to either depending on layout/version, and can append a
    count (e.g. 'Comment\\n42') which breaks an exact string match."""

    def _locate(d):
        candidates = d.find_elements(By.TAG_NAME, "button")
        for btn in candidates:
            try:
                label = (btn.get_attribute("aria-label") or "").strip().lower()
                text = (btn.text or "").strip().lower()
                visible = btn.is_displayed()
            except StaleElementReferenceException:
                continue

            if not visible:
                continue

            if text.startswith("comment") or "comment" in label:
                return btn
        return False

    try:
        return WebDriverWait(driver, timeout).until(_locate)
    except Exception:
        return None


def post_comment(driver, post_url: str, comment_text: str) -> bool:
    if not post_url:
        raise ValueError("post_url is required")

    driver.get(post_url)
    time.sleep(2)

    # Nudge a scroll to trigger any lazy-rendered engagement bar before searching
    driver.execute_script("window.scrollBy(0, 300);")
    time.sleep(1.5)

    try:
        action_comment_btn = _find_comment_button(driver)

        if not action_comment_btn:
            print("Comment button not found")
            # TEMP DEBUG — remove once this is confirmed working again.
            # Prints every button's aria-label/text so we can see what
            # LinkedIn is actually rendering right now.
            debug_buttons = [
                (b.get_attribute("aria-label") or b.text)
                for b in driver.find_elements(By.TAG_NAME, "button")
            ][:20]
            print("DEBUG: buttons on page:", debug_buttons)
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", action_comment_btn)
        time.sleep(0.8)
        driver.execute_script("arguments[0].click();", action_comment_btn)
        time.sleep(2.5)

        comment_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='comment' i]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", comment_box)
        time.sleep(0.5)
        _type_into_editor(driver, comment_box, comment_text)

        submit_btn = driver.execute_script("""
            var buttons = document.querySelectorAll('button');
            var best = null;
            var bestTop = -Infinity;
            for (var i = 0; i < buttons.length; i++) {
                var b = buttons[i];
                if ((b.innerText || '').trim().toLowerCase() !== 'comment') continue;
                if (b.disabled) continue;
                var rect = b.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) continue;
                if (rect.top > bestTop) {
                    bestTop = rect.top;
                    best = b;
                }
            }
            return best;
        """)

        if not submit_btn:
            print("Submit button not found")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)

        print("Comment posted successfully")
        return True

    except Exception as e:
        print(f"Failed to post comment: {e}")
        return False