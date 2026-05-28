import os
import threading
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
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
        script_lines = [
            "const el = document.getElementById(arguments[0]);",
            "if(!el) return false;",
            "const plot = el.querySelector('.js-plotly-plot') || el;",
            "if(plot && plot.data && plot.data.length>0) return true;",
            "// fallback: look for SVG traces or bars",
            "if(plot.querySelector && (",
            "plot.querySelector('g.trace') || plot.querySelector('path'))) return true;",
            "return false;",
        ]
        script = "".join(script_lines)
        try:
            return bool(driver.execute_script(script, graph_id))
        except WebDriverException:
            return False

    WebDriverWait(driver, timeout).until(_check)


def wait_for_element(driver, by, value, timeout: int = 15):
    """Wait for an element to be present in the DOM and return it.

    Uses Selenium's expected_conditions.presence_of_element_located so it
    works with client-side frameworks that attach elements asynchronously.
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def get_plotly_data_signature(driver, graph_id: str) -> str:
    """Return a lightweight signature of the graph content to detect updates."""
    script_lines = [
        "const el = document.getElementById(arguments[0]);",
        "if(!el) return null;",
        "const plot = el.querySelector('.js-plotly-plot') || el;",
        (
            "if(plot && plot.data) return plot.data.length + '|' + "
            "JSON.stringify(plot.data.map(d=>d.name||d.type||'')).slice(0,200);"
        ),
        "if(plot && plot.innerHTML) return plot.innerHTML.slice(0,200);",
        "return null;",
    ]
    script = "".join(script_lines)
    try:
        return driver.execute_script(script, graph_id)
    except WebDriverException:
        return None


def wait_for_stable_signature_raf(
    driver,
    element_id: str,
    signature_script: str,
    timeout: int = 15,
    stable_frames: int = 3,
):
    """Wait until a browser signature stays stable across animation frames.

    The check is executed in the page context via requestAnimationFrame so the
    wait tracks the browser's render loop instead of fixed sleeps or polling.
    """
    script = """
        const elementId = arguments[0];
        const signatureScript = arguments[1];
        const stableFrames = arguments[2];
        const timeoutMs = arguments[3];
        const done = arguments[arguments.length - 1];

        const start = performance.now();
        let lastSignature = null;
        let sameCount = 0;

        function readSignature() {
            const el = document.getElementById(elementId);
            if (!el) {
                return null;
            }

            try {
                return Function('el', signatureScript)(el);
            } catch (error) {
                return null;
            }
        }

        function tick() {
            const current = readSignature();

            if (current !== null && current === lastSignature) {
                sameCount += 1;
                if (sameCount >= stableFrames) {
                    done(current);
                    return;
                }
            } else {
                sameCount = 0;
            }

            lastSignature = current;

            if (performance.now() - start >= timeoutMs) {
                done(null);
                return;
            }

            requestAnimationFrame(tick);
        }

        requestAnimationFrame(tick);
    """
    return driver.execute_async_script(
        script,
        element_id,
        signature_script,
        stable_frames,
        timeout * 1000,
    )


def wait_for_plotly_graph_stable(driver, graph_id: str, timeout: int = 15):
    """Wait until a Plotly graph has settled across animation frames."""
    signature_script = """
        const plot = el.querySelector('.js-plotly-plot') || el;
        if (plot && plot.data) {
            return plot.data.length + '|' + JSON.stringify(
                plot.data.map(d => d.name || d.type || '')
            ).slice(0, 200);
        }
        if (plot && plot.innerHTML) {
            return plot.innerHTML.slice(0, 200);
        }
        return null;
    """
    return wait_for_stable_signature_raf(
        driver,
        graph_id,
        signature_script,
        timeout=timeout,
    )


def wait_for_text_stable(driver, element_id: str, timeout: int = 15):
    """Wait until a text container content remains stable across frames."""
    signature_script = """
        return (el.textContent || '').trim();
    """
    return wait_for_stable_signature_raf(
        driver,
        element_id,
        signature_script,
        timeout=timeout,
    )


def click_slider_by_percent(driver, slider_id: str, percent: float) -> None:
    """Click a Dash/rc-slider at `percent` (0.0-1.0) of its width.

    This performs a click on the slider track; it is a best-effort action that
    works for the common rc-slider markup used by Dash sliders.
    """
    slider = driver.find_element(By.ID, slider_id)

    # ensure visible in viewport
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider)
    except WebDriverException:
        pass

    # attempt strategies in order; helpers return True on success
    if _try_handle_keyboard(slider, percent):
        return

    if _dispatch_js_click(driver, slider, max(0.0, min(1.0, percent))):
        return

    if _offset_click(driver, slider, percent):
        return

    # give up silently; tests should handle lack of interaction
    return


def _try_handle_keyboard(slider, percent: float) -> bool:
    """Try moving the first slider handle with keyboard arrows. Returns True on success."""
    try:
        if not (handles := slider.find_elements(By.CSS_SELECTOR, ".rc-slider-handle")):
            return False
        handle = handles[0]
        handle.click()
        steps = int(max(1, min(100, round(percent * 20))))
        key = Keys.ARROW_RIGHT if percent >= 0.5 else Keys.ARROW_LEFT
        for _ in range(steps):
            handle.send_keys(key)
        return True
    except WebDriverException:
        return False


def _dispatch_js_click(driver, slider, percent: float) -> bool:
    """Dispatch a synthetic click event at `percent` of `slider` bounding box.

    Returns True on success, False on failure.
    """
    script_lines = [
        "const el = arguments[0];",
        "const rect = el.getBoundingClientRect();",
        "const x = rect.left + rect.width * arguments[1];",
        "const y = rect.top + rect.height/2;",
        "const ev = new MouseEvent('click', {bubbles: true, clientX: x, clientY: y});",
        "el.dispatchEvent(ev);",
    ]
    try:
        driver.execute_script("".join(script_lines), slider, percent)
        return True
    except WebDriverException:
        return False


def _offset_click(driver, slider, percent: float) -> bool:
    """Perform an ActionChains offset click on the slider at `percent` position.

    Returns True on success, False on failure.
    """
    try:
        try:
            track = slider.find_element(By.CSS_SELECTOR, ".rc-slider")
        except NoSuchElementException:
            track = slider
        size = track.size
        p = max(0.0, min(1.0, percent))
        x_offset = int(size["width"] * p)
        y_offset = int(size["height"] / 2)
        ActionChains(driver).move_to_element_with_offset(
            track, x_offset, y_offset
        ).click().perform()
        return True
    except WebDriverException:
        return False


def measure_action_time(driver, action_fn, ready_check_fn, timeout: int = 15) -> float:
    """Measure milliseconds elapsed between performing `action_fn()` and
    `ready_check_fn()` returning truthy. Uses `performance.now()` in page context
    to get high-resolution timings.
    """
    # get start timestamp from page
    try:
        start = driver.execute_script("return performance.now();")
    except WebDriverException:
        # fallback to python time
        start = time.perf_counter() * 1000.0

    # perform the action
    action_fn()

    # wait for ready_check to become truthy; the callback owns the wait logic
    ready_value = ready_check_fn()
    if not ready_value:
        raise TimeoutError(
            f"Timed out waiting for action to settle after {timeout} seconds"
        )

    try:
        end = driver.execute_script("return performance.now();")
    except WebDriverException:
        end = time.perf_counter() * 1000.0

    return float(end) - float(start)


def get_slider_value(driver, slider_id: str):
    """Get the current numeric value of a Dash RangeSlider or Slider component.

    Returns the value as a float or the raw value if extraction fails.
    """
    script = (
        "const el = document.getElementById(arguments[0]);"
        "if (el && el.__dash_loaded_props) {"
        "  const props = el.__dash_loaded_props;"
        "  if (props.value !== undefined) return props.value;"
        "}"
        "return null;"
    )
    try:
        val = driver.execute_script(script, slider_id)
        if val is not None:
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
        "if (el && el.__dash_loaded_props) {"
        "  const props = el.__dash_loaded_props;"
        "  if (props.value !== undefined) return props.value;"
        "}"
        "return null;"
    )
    try:
        return driver.execute_script(script, dropdown_id)
    except WebDriverException:
        return None


def wait_for_page_ready(driver, graph_ids: list, timeout: int = 15) -> None:
    """Wait for a page to be fully ready by checking all specified graphs are rendered.

    Args:
        driver: Selenium WebDriver
        graph_ids: List of Plotly graph element IDs to wait for
        timeout: Maximum time to wait in seconds
    """
    for graph_id in graph_ids:
        wait_for_plotly_graph(driver, graph_id, timeout=timeout)
