from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ChatSiteAdapter:
    """Generic adapter — works with any chat site given three CSS selectors:
    where to type, what to click to send, and where replies appear."""

    def __init__(self, url, input_css, send_css, reply_css):
        self.url = url
        self.input_selector = (By.CSS_SELECTOR, input_css)
        self.send_selector = (By.CSS_SELECTOR, send_css)
        self.reply_selector = (By.CSS_SELECTOR, reply_css)

    def send_message(self, driver, message: str, timeout: int = 60) -> str:
        box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(self.input_selector)
        )
        box.click()
        box.send_keys(message)

        prev_count = len(driver.find_elements(*self.reply_selector))

        send_btn = driver.find_element(*self.send_selector)
        send_btn.click()

        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(*self.reply_selector)) > prev_count
        )
        # basic settle time for streaming replies to finish typing out
        self._wait_for_reply_to_settle(driver, timeout)

        replies = driver.find_elements(*self.reply_selector)
        return replies[-1].text

    def _wait_for_reply_to_settle(self, driver, timeout, poll=1.0):
        import time
        start = time.time()
        last_text = None
        while time.time() - start < timeout:
            replies = driver.find_elements(*self.reply_selector)
            if not replies:
                time.sleep(poll)
                continue
            current = replies[-1].text
            if current == last_text:
                return
            last_text = current
            time.sleep(poll)