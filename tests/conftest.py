import os
import threading

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from werkzeug.serving import make_server

from app import app as noplp_app

# Ensure CHROMEWEBDRIVER path (if provided) is added to PATH so Selenium can find chromedriver.
# Tests can set the CHROMEWEBDRIVER env var before running pytest. If it's set, add it to PATH.
if chrome_driver_dir := os.environ.get("CHROMEWEBDRIVER"):
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + chrome_driver_dir


def _build_chrome_options():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    return options


@pytest.fixture(scope="module")
def live_server():
    server = make_server("127.0.0.1", 0, noplp_app.server)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    thread.join(timeout=5)


@pytest.fixture
def browser():
    driver = webdriver.Chrome(options=_build_chrome_options())
    yield driver
    driver.quit()
