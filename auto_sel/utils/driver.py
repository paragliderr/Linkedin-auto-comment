from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.common.exceptions import WebDriverException


def common_options(options):

    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--remote-debugging-port=9222")

    # for apple silicon
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--renderer-process-limit=1")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")

    options.add_experimental_option(
        "prefs",
        {
            "profile.content_settings.exceptions.clipboard": {
                "*": {"setting": 2}
            }
        }
    )

    return options

def create_edge_driver():

    options = EdgeOptions()
    common_options(options)

    driver = webdriver.Edge(
        service=EdgeService(
            EdgeChromiumDriverManager().install()
        ),
        options=options
    )

    driver.set_page_load_timeout(90)
    driver.set_script_timeout(60)

    return driver

def create_chrome_driver():

    options = webdriver.ChromeOptions()
    common_options(options)

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    driver.set_page_load_timeout(90)
    driver.set_script_timeout(60)

    return driver


def get_driver():

    try:
        print("Launching Microsoft Edge...")
        return create_edge_driver()

    except Exception as e:
        print(f"Edge unavailable: {e}")

    try:
        print("Launching Google Chrome...")
        return create_chrome_driver()

    except Exception as e:
        print(f"Chrome unavailable: {e}")

    raise RuntimeError(
        "No supported browser found. Please install Microsoft Edge or Google Chrome."
    )