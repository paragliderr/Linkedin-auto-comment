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
    """
    Type text into a Quill editor using JS + clipboard injection.
    Avoids ActionChains and send_keys which crash ChromeDriver on Apple Silicon.
    """
    # Focus the box first    driver.execute_script("arguments[0].focus();", box)
    time.sleep(0.3)

    driver.execute_script("""
        var el = arguments[0];
        var text = arguments[1];
        el.focus();
        // Use execCommand so Quill registers the change as a real input event
        document.execCommand('selectAll', false, null);
        document.execCommand('insertText', false, text);
    """, box, text)
    time.sleep(0.5)


def post_comment(driver, post_url: str, comment_text: str) -> bool:
    if not post_url:
        raise ValueError("post_url is required")

    driver.get(post_url)
    time.sleep(4)

    try:
        comment_btn = _find_button_by_text(driver, "Comment")
        if not comment_btn:
            print("Comment button not found")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", comment_btn)
        time.sleep(0.8)
        driver.execute_script("arguments[0].click();", comment_btn)
        time.sleep(2.5)

        comment_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", comment_box)
        time.sleep(0.5)
        _type_into_editor(driver, comment_box, comment_text)
        time.sleep(1)

        submit_btn = _find_button_by_text(driver, "post", "submit", "done")
        if not submit_btn:
            print("Submit button not found")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", submit_btn)
        time.sleep(2)
        return True

    except Exception as e:
        print(f"Failed to post comment: {e}")
        return False