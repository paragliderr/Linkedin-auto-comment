import pickle
from auto_sel.utils.driver import get_driver
import os 
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
        cookie_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.pkl")
        with open(cookie_path, "wb") as file:
            pickle.dump(driver.get_cookies(), file)
        print("\nSession saved successfully!")
        print("Cookies stored in auth/cookies.pkl")
    except Exception as e:
        print(f"\nError during login: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    login_and_save_session()