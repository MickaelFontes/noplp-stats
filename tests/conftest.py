import os

from selenium.webdriver.chrome.options import Options

# Ensure CHROMEWEBDRIVER path (if provided) is added to PATH so Selenium can find chromedriver
# Tests can set the CHROMEWEBDRIVER env var before running pytest. If it's set, add it to PATH.
chrome_driver_dir = os.environ.get("CHROMEWEBDRIVER")
if chrome_driver_dir:
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + chrome_driver_dir


def pytest_setup_options():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    return options
