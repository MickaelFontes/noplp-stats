from selenium.webdriver.chrome.options import Options
import pytest
from pyvirtualdisplay import Display


def pytest_setup_options():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    return options


@pytest.fixture(autouse=True)
def web_browser_display():
    display = Display(visible=False, size=(1920, 1080))
    display.start()

    # Return browser instance to test case:
    yield

    display.stop()
