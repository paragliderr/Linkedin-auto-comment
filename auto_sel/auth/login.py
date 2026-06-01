import pickle
from utils.driver import get_driver
def login_and_save_session():
    driver = get_driver()
    try:
        driver.get("https://www.linkedin.com/login")
        print("\nLinkedIn login page opened.\n")
        input(
            "Login manually in the browser.\n"
            "After you successfully reach the LinkedIn feed/home page,\n"
            "press Enter here..."
        )
        with open("auth/cookies.pkl", "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        print("\nSession saved successfully!")
        print("Cookies stored in auth/cookies.pkl")
    except Exception as e:
        print(f"\nError during login: {e}")
    finally:
        driver.quit()