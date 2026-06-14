import time
import pyautogui
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
    time.sleep(1.5)


def _real_click(driver, element):
    """
    OS-level mouse click using pyautogui.
    Gets the element's position on screen and clicks it directly.
    This bypasses any JS/React interception.
    """
    rect = driver.execute_script("""
        var r = arguments[0].getBoundingClientRect();
        return { x: r.left, y: r.top, w: r.width, h: r.height };
    """, element)

    win_x = driver.execute_script("return window.screenX;")
    win_y = driver.execute_script("return window.screenY;")

    chrome_toolbar_height = 85

    click_x = win_x + rect['x'] + rect['w'] / 2
    click_y = win_y + chrome_toolbar_height + rect['y'] + rect['h'] / 2

    print(f"  Clicking at screen coords ({click_x:.0f}, {click_y:.0f})")
    pyautogui.click(click_x, click_y)


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
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='comment']")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", comment_box)
        time.sleep(0.5)
        _type_into_editor(driver, comment_box, comment_text)

        submit_btn = None
        for _ in range(10):
            for btn in driver.find_elements(By.TAG_NAME, "button"):
                try:
                    if btn.text.strip().lower() == "comment":
                        disabled = driver.execute_script("return arguments[0].disabled;", btn)
                        if not disabled:
                            submit_btn = btn
                            break
                except StaleElementReferenceException:
                    continue
            if submit_btn:
                break
            time.sleep(0.5)

        if not submit_btn:
            print("Submit button never became enabled")
            return False

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit_btn)
        time.sleep(0.5)

        _real_click(driver, submit_btn)
        time.sleep(2)

        try:
            WebDriverWait(driver, 5).until_not(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[contenteditable='true'][aria-label*='comment']")
                )
            )
            print("Comment posted successfully")
            return True
        except Exception:
            print("Comment box still visible after click — may have failed")
            return False

    except Exception as e:
        print(f"Failed to post comment: {e}")
        return False