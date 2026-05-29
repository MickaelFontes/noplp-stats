import os
import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    WebDriverException,
)
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

    if os.path.exists("/.dockerenv"):
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--remote-debugging-pipe")

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
    chromedriver_log_path = os.environ.get(
        "CHROMEDRIVER_LOG_PATH", os.path.join("tests", "artifacts", "chromedriver.log")
    )
    os.makedirs(os.path.dirname(chromedriver_log_path), exist_ok=True)

    service_args = []
    if os.environ.get("CHROMEDRIVER_VERBOSE", "0").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }:
        service_args.append("--verbose")

    service = Service(
        service_args=service_args,
        log_output=chromedriver_log_path,
    )

    driver = webdriver.Chrome(service=service, options=_build_chrome_options())
    driver.set_window_size(1280, 720)
    yield driver
    driver.quit()


def wait_for_element(driver, by, value, timeout: int = 15):
    """Wait for an element to be present in the DOM and return it.

    Uses Selenium's expected_conditions.presence_of_element_located so it
    works with client-side frameworks that attach elements asynchronously.
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def _install_network_tracker(driver) -> None:
    """Install a lightweight network tracker for fetch/XHR and resource entries."""
    script = """
        if (!window.__networkTrackerInstalled) {
            window.__networkTrackerInstalled = true;
            window.__inflightRequests = 0;
            window.__lastResourceCount = performance.getEntriesByType('resource').length;

            const originalFetch = window.fetch;
            window.fetch = function() {
                window.__inflightRequests += 1;
                return originalFetch.apply(this, arguments)
                    .finally(() => { window.__inflightRequests -= 1; });
            };

            const originalOpen = XMLHttpRequest.prototype.open;
            const originalSend = XMLHttpRequest.prototype.send;

            XMLHttpRequest.prototype.open = function() {
                this.__trackRequest = true;
                return originalOpen.apply(this, arguments);
            };

            XMLHttpRequest.prototype.send = function() {
                if (this.__trackRequest) {
                    window.__inflightRequests += 1;
                    this.addEventListener('loadend', () => { window.__inflightRequests -= 1; });
                }
                return originalSend.apply(this, arguments);
            };
        }
    """
    driver.execute_script(script)


def wait_for_network_idle(driver, timeout: int = 10, max_quiet_ms: int = 5000) -> int:
    """Wait until all network requests finish and return elapsed wait time in ms.

    Returns 0 if the timeout is reached before the page becomes idle.
    """
    _install_network_tracker(driver)
    start = time.perf_counter()
    quiet_start = None
    last_resource_count = None

    while time.perf_counter() - start < timeout:
        inflight, resource_count, ready_state = driver.execute_script("""
            return [
                window.__inflightRequests || 0,
                performance.getEntriesByType('resource').length,
                document.readyState
            ];
            """)

        if last_resource_count != resource_count:
            last_resource_count = resource_count
            quiet_start = time.perf_counter()

        if inflight == 0 and ready_state == "complete" and quiet_start is not None:
            if (
                (time.perf_counter() - quiet_start) * 1000
            ) >= max_quiet_ms:  # noqa: PLR2004
                return int((quiet_start - start) * 1000)

        time.sleep(0.05)

    return 0


def get_slider_value(driver, slider_id: str):
    """Get the current numeric value of a Dash RangeSlider or Slider component.

    Returns the value as a float or the raw value if extraction fails.
    """
    script = (
        "const el = document.getElementById(arguments[0]);"
        "if (!el) return null;"
        "if (el.__dash_loaded_props && el.__dash_loaded_props.value !== undefined) {"
        "  return el.__dash_loaded_props.value;"
        "}"
        "const handle = el.querySelector('.rc-slider-handle');"
        "if (handle && handle.hasAttribute('aria-valuenow')) {"
        "  return parseFloat(handle.getAttribute('aria-valuenow'));"
        "}"
        "return null;"
    )
    try:
        if (val := driver.execute_script(script, slider_id)) is not None:
            return float(val) if isinstance(val, (int, float)) else val
    except (WebDriverException, ValueError):
        pass
    return None


def get_dropdown_value(driver, dropdown_id: str):
    """Get the current selected value of a Dash Dropdown component.

    Returns the selected value (typically a string like a song title).
    """
    script = (
        "const el = document.getElementById(arguments[0]);"
        "if (!el) return null;"
        "if (el.__dash_loaded_props && el.__dash_loaded_props.value !== undefined) {"
        "  return el.__dash_loaded_props.value;"
        "}"
        "const singleValue = el.querySelector('.Select-value-label, .react-select__single-value');"
        "if (singleValue) {"
        "  return (singleValue.textContent || '').trim();"
        "}"
        "return null;"
    )
    try:
        return driver.execute_script(script, dropdown_id)
    except WebDriverException:
        return None
