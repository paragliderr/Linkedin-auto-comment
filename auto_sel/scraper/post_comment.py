import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException


def _find_submit_button(driver):
    selectors = [
        "button.comments-comment-box__submit-button--cr",
        "button[class*='comments-comment-box__submit']",
    ]
    for sel in selectors:
        btns = driver.find_elements(By.CSS_SELECTOR, sel)
        if btns:
            return btns[0]
    return None

def _type_into_editor(driver, box, text):
    time.sleep(0.3)

    driver.execute_script("arguments[0].focus();", box)
    time.sleep(0.2)

    driver.execute_script("""
        var el = arguments[0];
        var text = arguments[1];
        el.innerText = text;
    """, box, text)
    time.sleep(0.3)

    driver.execute_script("""
        var el = arguments[0];
        el.dispatchEvent(new Event('input', { bubbles: true }));
    """, box)
    time.sleep(0.8)


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
        
        is_disabled = driver.execute_script("return arguments[0].disabled;", submit_btn)
        print(f"Submit button disabled state: {is_disabled}")

        if is_disabled:
            print("Submit button is disabled — text may not have registered")
            return False



    except Exception as e:
        print(f"Failed to post comment: {e}")
        return False