from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")                  
    options.add_argument("--remote-debugging-port=9222")   
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")

    options.add_experimental_option("prefs", {
        "profile.content_settings.exceptions.clipboard": {"*": {"setting": 2}}
    })

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.set_page_load_timeout(60)
    driver.set_script_timeout(30)

    return driver