import os
import sys
from pathlib import Path


def configure_playwright():
    """
    Makes Playwright use the correct browser location
    in development and in the packaged EXE.
    """

    if getattr(sys, "frozen", False):
        browser_path = Path(sys._MEIPASS) / "playwright-browsers"
    else:
        browser_path = (
            Path(__file__).resolve().parent.parent
            / "playwright-browsers"
        )
    print(f"Playwright browser path: {browser_path}")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browser_path)