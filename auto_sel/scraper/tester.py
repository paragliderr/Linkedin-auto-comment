import time
from auto_sel.auth.session import load_session
from auto_sel.scraper.post_comment import post_comment

driver = load_session()
url = "https://www.linkedin.com/posts/eric-vyacheslav-156273169_a-40-billion-payments-company-gave-away-share-7470868191594975232-MOYD/?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFjzAmoBTIQ7Xff2XUBLFyzZJE5IONhRH6I"

driver.get(url)
time.sleep(5)
input("Browser open — press Enter after you manually click Comment and see the box open...")

# Now check if Selenium can even see the box
from selenium.webdriver.common.by import By
boxes = driver.find_elements(By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']")
print(f"Found {len(boxes)} editor boxes")

if boxes:
    box = boxes[0]
    driver.execute_script("arguments[0].focus(); arguments[0].innerText = arguments[1];", box, "test comment")
    time.sleep(1)
    print("Text set, check browser")
    input("Press Enter to continue...")