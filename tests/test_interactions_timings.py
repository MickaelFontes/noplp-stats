import json
import os
import time
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import (
    click_slider_by_percent,
    wait_for_element,
    measure_action_time,
    get_slider_value,
    get_dropdown_value,
    wait_for_plotly_graph_stable,
    wait_for_plotly_graph_change_stable,
    wait_for_text_change_stable,
)


def _ensure_artifacts_dir():
    path = os.path.join("tests", "artifacts")
    os.makedirs(path, exist_ok=True)
    return path


def _write_timing_artifact(prefix: str, payload: dict) -> None:
    artifacts_dir = _ensure_artifacts_dir()
    filename = os.path.join(artifacts_dir, f"{prefix}-{int(time.time())}.json")
    with open(filename, "w", encoding="utf8") as handle:
        json.dump(payload, handle)


def test_global_nb_songs_slider_updates_and_timing(browser, live_server):
    """Navigate to /global, measure initial load, change `nb-songs` slider and measure update time."""
    base = live_server
    url = urljoin(base, "/global")

    # Measure initial page load time (from navigation to graph ready)
    load_start = time.perf_counter() * 1000.0
    browser.get(url)
    initial_signature = wait_for_plotly_graph_stable(browser, "graph", timeout=15)
    assert initial_signature is not None
    load_end = time.perf_counter() * 1000.0
    initial_load_ms = load_end - load_start

    # Get initial state
    value_before = get_slider_value(browser, "nb-songs")

    # Perform slider interaction
    def action():
        # Ensure slider is visible and clickable
        slider = browser.find_element(By.ID, "nb-songs")
        browser.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", slider
        )
        # Wait for slider to be in viewport (presence + visibility)
        WebDriverWait(browser, 5).until(
            EC.visibility_of_element_located((By.ID, "nb-songs"))
        )
        click_slider_by_percent(browser, "nb-songs", 0.8)

    def ready_check():
        return wait_for_plotly_graph_change_stable(
            browser,
            "graph",
            initial_signature,
            timeout=25,
        )

    elapsed_ms = measure_action_time(browser, action, ready_check, timeout=20)

    # Verify the slider value actually changed
    value_after = get_slider_value(browser, "nb-songs")
    value_changed = value_after != value_before

    _write_timing_artifact(
        "timing-global-nb-songs",
        {
            "page": "/global",
            "initial_page_load_ms": initial_load_ms,
            "initial_graph_signature": initial_signature,
            "slider_id": "nb-songs",
            "value_before": value_before,
            "value_after": value_after,
            "value_changed": value_changed,
            "action": "slider position change (0->0.8)",
            "interaction_render_time_ms": elapsed_ms,
        },
    )


def test_training_dropdown_selection_timing(browser, live_server):
    """Navigate to /training, measure initial load, change dropdown and measure render time."""
    base = live_server
    url = urljoin(base, "/training")

    # Measure initial page load time
    load_start = time.perf_counter() * 1000.0
    browser.get(url)
    # Wait for dropdown specifically
    dropdown_id = "dropdown-song-training"
    # Wait for the dropdown element by id (legacy react-select selector removed)
    dd_control = wait_for_element(browser, By.ID, dropdown_id, timeout=15)
    load_end = time.perf_counter() * 1000.0
    initial_load_ms = load_end - load_start

    # Get initial state
    value_before = get_dropdown_value(browser, dropdown_id)
    text_before = browser.find_element(By.ID, "verified-lyrics").text

    selected_value = None

    def action():
        nonlocal selected_value
        # Ensure dropdown control is visible and clickable
        browser.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", dd_control
        )
        WebDriverWait(browser, 5).until(EC.visibility_of(dd_control))
        # Click to open dropdown
        browser.execute_script("arguments[0].click();", dd_control)
        # Wait for at least one option to appear
        WebDriverWait(browser, 5).until(
            EC.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR,
                    "div.Select-option, div[role='option'], .VirtualizedSelectOption",
                )
            )
        )
        option_nodes = browser.find_elements(
            By.CSS_SELECTOR,
            "div.Select-option, div[role='option'], .VirtualizedSelectOption",
        )
        for option in option_nodes:
            option_text = option.text.strip()
            if option_text and option_text != value_before:
                selected_value = option_text
                option.click()
                break
        if selected_value is None:
            dd_control.send_keys(Keys.ARROW_DOWN)
            dd_control.send_keys(Keys.ENTER)

    def ready_check():
        return wait_for_text_change_stable(
            browser,
            "verified-lyrics",
            text_before,
            timeout=10,
        )

    elapsed_ms = measure_action_time(browser, action, ready_check, timeout=10)

    # Verify dropdown value changed
    value_after = get_dropdown_value(browser, dropdown_id)
    value_changed = value_after != value_before

    _write_timing_artifact(
        "timing-training-dropdown",
        {
            "page": "/training",
            "initial_page_load_ms": initial_load_ms,
            "dropdown_id": dropdown_id,
            "value_before": value_before,
            "value_after": value_after,
            "text_before": text_before,
            "text_after": browser.find_element(By.ID, "verified-lyrics").text,
            "selected_option_text": selected_value,
            "value_changed": value_changed,
            "action": "dropdown selection change",
            "interaction_render_time_ms": elapsed_ms,
        },
    )
