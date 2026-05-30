import json
import os
import threading
import time
from datetime import datetime, timezone

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from werkzeug.serving import make_server

from app import app as noplp_app

# Ensure CHROMEWEBDRIVER path (if provided) is added to PATH so Selenium can find chromedriver.
# Tests can set the CHROMEWEBDRIVER env var before running pytest. If it's set, add it to PATH.
if chrome_driver_dir := os.environ.get("CHROMEWEBDRIVER"):
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + chrome_driver_dir


def _ensure_artifacts_dir():
    path = os.path.join("tests", "artifacts")
    os.makedirs(path, exist_ok=True)
    return path


def _write_timing_results(filename: str, payload: dict) -> None:
    with open(filename, "w", encoding="utf8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=False)


def pytest_configure(config):
    config._timing_results = {}


def pytest_sessionfinish(session, exitstatus):
    timing_results = getattr(session.config, "_timing_results", {})
    artifact_name = datetime.now(timezone.utc).strftime(
        "timing-results-%Y-%m-%dT%H-%M-%SZ.json"
    )
    artifact_path = os.path.join(_ensure_artifacts_dir(), artifact_name)
    _write_timing_results(
        artifact_path,
        {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "pytest_exitstatus": exitstatus,
            "tests": timing_results,
        },
    )


def record_timing_result(request, payload: dict) -> None:
    test_name = getattr(request.node, "originalname", request.node.name)
    request.config._timing_results[test_name] = payload


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
        lambda current_driver: current_driver.find_element(by, value)
    )


def wait_for_dash_idle(driver, timeout: int = 10) -> int:
    """Wait until Dash finishes its current loading state and return elapsed ms."""
    start = time.perf_counter()
    try:
        WebDriverWait(driver, timeout).until(
            lambda current_driver: current_driver.execute_script(
                "return document.readyState"
            )
            == "complete"
            and not current_driver.find_elements(
                By.CSS_SELECTOR, "._dash-loading-callback"
            )
        )
    except TimeoutException:
        return 0

    return int((time.perf_counter() - start) * 1000)


def measure_until_dash_ready(driver, trigger_fn, timeout: int = 10) -> int:
    """Measure a trigger until Dash reaches a usable idle state."""
    start = time.perf_counter()
    trigger_fn()

    if not wait_for_dash_idle(driver, timeout=timeout):
        return 0

    return int((time.perf_counter() - start) * 1000)


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
