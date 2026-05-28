import os
import threading

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
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
    driver.set_window_size(1280, 720)
    yield driver
    driver.quit()


def wait_for_plotly_graph(driver, graph_id: str, timeout: int = 15) -> None:
    """Wait until a Plotly/Dash graph with given `graph_id` has rendered data.

    This uses a JS check that looks for Plotly data or graph-like SVG elements.
    """

    def _check(driver):
        script = (
            "const el = document.getElementById(arguments[0]);"
            "if(!el) return false;"
            "const plot = el.querySelector('.js-plotly-plot') || el;"
            "if(plot && plot.data && plot.data.length>0) return true;"
            "// fallback: look for SVG traces or bars"
            "if(plot.querySelector && (plot.querySelector('g.trace') || plot.querySelector('path'))) return true;"
            "return false;"
        )
        try:
            return bool(driver.execute_script(script, graph_id))
        except Exception:
            return False

    WebDriverWait(driver, timeout).until(lambda d: _check(d))


def get_plotly_data_signature(driver, graph_id: str) -> str:
    """Return a lightweight signature of the graph content to detect updates."""
    script = (
        "const el = document.getElementById(arguments[0]);"
        "if(!el) return null;"
        "const plot = el.querySelector('.js-plotly-plot') || el;"
        "if(plot && plot.data) return plot.data.length + '|' + JSON.stringify(plot.data.map(d=>d.name||d.type||'')).slice(0,200);"
        "if(plot && plot.innerHTML) return plot.innerHTML.slice(0,200);"
        "return null;"
    )
    try:
        return driver.execute_script(script, graph_id)
    except Exception:
        return None


def click_slider_by_percent(driver, slider_id: str, percent: float) -> None:
    """Click a Dash/rc-slider at `percent` (0.0-1.0) of its width.

    This performs a click on the slider track; it is a best-effort action that
    works for the common rc-slider markup used by Dash sliders.
    """
    slider = driver.find_element(By.ID, slider_id)
    # try to find the visible track element used by rc-slider
    try:
        track = slider.find_element(By.CSS_SELECTOR, ".rc-slider")
    except Exception:
        track = slider

    size = track.size
    # clamp percent
    p = max(0.0, min(1.0, percent))
    x_offset = int(size["width"] * p)
    y_offset = int(size["height"] / 2)
    ActionChains(driver).move_to_element_with_offset(
        track, x_offset, y_offset
    ).click().perform()


def measure_action_time(driver, action_fn, ready_check_fn, timeout: int = 15) -> float:
    """Measure milliseconds elapsed between performing `action_fn()` and
    `ready_check_fn()` returning truthy. Uses `performance.now()` in page context
    to get high-resolution timings.
    """
    # get start timestamp from page
    try:
        start = driver.execute_script("return performance.now();")
    except Exception:
        # fallback to python time
        import time

        start = time.perf_counter() * 1000.0

    # perform the action
    action_fn()

    # wait for ready_check to become truthy
    WebDriverWait(driver, timeout).until(lambda d: ready_check_fn())

    try:
        end = driver.execute_script("return performance.now();")
    except Exception:
        import time

        end = time.perf_counter() * 1000.0

    return float(end) - float(start)
