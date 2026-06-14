import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def _find_button_by_text(driver, *labels):
    for btn in driver.find_elements(By.TAG_NAME, "button"):
        try:
            if btn.text.strip().lower() in [l.lower() for l in labels]:
                return btn
        except StaleElementReferenceException:
            continue
    return None


def _type_into_editor(driver, box, text):
    driver.execute_script("arguments[0].focus();", box)
    time.sleep(0.2)
    driver.execute_script("arguments[0].innerText = arguments[1];", box, text)
    time.sleep(0.3)
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", box
    )
    time.sleep(1)  # give Quill time to register the input and enable the submit button


def post_comment(driver, post_url: str, comment_text: str) -> bool:
    if not post_url:
        raise ValueError("post_url is required")

    driver.get(post_url)
    time.sleep(4)

    try:
        # Step 1 — open the comment box
        comment_btn = _find_button_by_text(driver, "Comment")
        if not comment_btn:
            print("Comment button not found")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", comment_btn)
        time.sleep(0.8)
        driver.execute_script("arguments[0].click();", comment_btn)
        time.sleep(2.5)

        # Step 2 — type into the editor
        comment_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='comment']")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", comment_box)
        time.sleep(0.5)
        _type_into_editor(driver, comment_box, comment_text)

        # Step 3 — find submit button globally after typing
        # After clicking Comment and typing, there are now TWO "Comment" buttons:
        # the action bar one (disabled/hidden) and the submit one (enabled).
        # We pick the first enabled one.
        submit_btn = None
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            try:
                if btn.text.strip().lower() == "comment":
                    is_disabled = driver.execute_script("return arguments[0].disabled;", btn)
                    if not is_disabled:
                        submit_btn = btn
                        break
            except StaleElementReferenceException:
                continue

        if not submit_btn:
            print("Submit button not found or still disabled — text may not have registered")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        return True

    except Exception as e:
        print(f"Failed to post comment: {e}")
        return False