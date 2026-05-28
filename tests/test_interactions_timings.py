import json
import os
import time
from urllib.parse import urljoin

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tests.conftest import (
    click_slider_by_percent,
    wait_for_element,
    measure_action_time,
    get_slider_value,
    get_dropdown_value,
    wait_for_plotly_graph_stable,
    wait_for_text_stable,
)


def _ensure_artifacts_dir():
    path = os.path.join("tests", "artifacts")
    os.makedirs(path, exist_ok=True)
    return path


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
        click_slider_by_percent(browser, "nb-songs", 0.8)

    def ready_check():
        sig_after = wait_for_plotly_graph_stable(browser, "graph", timeout=20)
        if sig_after and sig_after != initial_signature:
            return sig_after
        return None

    elapsed_ms = measure_action_time(browser, action, ready_check, timeout=20)

    # Verify the slider value actually changed
    value_after = get_slider_value(browser, "nb-songs")
    value_changed = value_after != value_before

    artifacts_dir = _ensure_artifacts_dir()
    out = {
        "page": "/global",
        "initial_page_load_ms": initial_load_ms,
        "initial_graph_signature": initial_signature,
        "slider_id": "nb-songs",
        "value_before": value_before,
        "value_after": value_after,
        "value_changed": value_changed,
        "action": "slider position change (0->0.8)",
        "interaction_render_time_ms": elapsed_ms,
    }
    fname = os.path.join(
        artifacts_dir, f"timing-global-nb-songs-{int(time.time())}.json"
    )
    with open(fname, "w", encoding="utf8") as fh:
        json.dump(out, fh)


def test_training_dropdown_selection_timing(browser, live_server):
    """Navigate to /training, measure initial load, change dropdown and measure render time."""
    base = live_server
    url = urljoin(base, "/training")

    # Measure initial page load time
    load_start = time.perf_counter() * 1000.0
    browser.get(url)
    # Wait for dropdown specifically
    dropdown_id = "dropdown-song-training"
    dd = wait_for_element(browser, By.ID, dropdown_id, timeout=15)
    load_end = time.perf_counter() * 1000.0
    initial_load_ms = load_end - load_start

    # Get initial state
    value_before = get_dropdown_value(browser, dropdown_id)
    text_before = browser.find_element(By.ID, "verified-lyrics").text

    # Define dropdown interaction: open and select first available option
    selected_value = None

    def action():
        nonlocal selected_value
        dd.click()
        time.sleep(0.3)  # Give menu time to render
        try:
            # Pick the first option that differs from the current value.
            option_nodes = browser.find_elements(
                By.CSS_SELECTOR,
                "div.Select-option, div[role='option']",
            )
            for option in option_nodes:
                option_text = option.text.strip()
                if option_text and option_text != value_before:
                    selected_value = option_text
                    option.click()
                    break
            if selected_value is None:
                dd.send_keys(Keys.ARROW_DOWN)
                dd.send_keys(Keys.ENTER)
        except NoSuchElementException:
            pass

    def ready_check():
        content = wait_for_text_stable(browser, "verified-lyrics", timeout=10)
        if content and content != text_before:
            return content
        return None

    elapsed_ms = measure_action_time(browser, action, ready_check, timeout=10)

    # Verify dropdown value changed
    value_after = get_dropdown_value(browser, dropdown_id)
    value_changed = value_after != value_before

    artifacts_dir = _ensure_artifacts_dir()
    out = {
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
    }
    fname = os.path.join(
        artifacts_dir, f"timing-training-dropdown-{int(time.time())}.json"
    )
    with open(fname, "w", encoding="utf8") as fh:
        json.dump(out, fh)
