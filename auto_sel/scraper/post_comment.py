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


def post_comment(driver, post_url: str, comment_text: str) -> bool:
    if not post_url:
        raise ValueError("post_url is required")

    driver.get(post_url)
    time.sleep(4)

    try:

        action_comment_btn = None
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            try:
                if btn.text.strip().lower() == "comment":
                    action_comment_btn = btn
                    break
            except StaleElementReferenceException:
                continue

        if not action_comment_btn:
            print("Comment button not found")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", action_comment_btn)
        time.sleep(0.8)
        driver.execute_script("arguments[0].click();", action_comment_btn)
        time.sleep(2.5)
        comment_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='comment']")
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