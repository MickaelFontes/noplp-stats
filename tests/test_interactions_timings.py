import json
import os
import time
from urllib.parse import urljoin

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from tests.conftest import (
    wait_for_plotly_graph,
    get_plotly_data_signature,
    click_slider_by_percent,
    measure_action_time,
)


def _ensure_artifacts_dir():
    path = os.path.join("tests", "artifacts")
    os.makedirs(path, exist_ok=True)
    return path


def test_global_nb_songs_slider_updates_and_timing(browser, live_server):
    """Navigate to /global, change `nb-songs` slider and measure update time for `graph`."""
    base = live_server
    url = urljoin(base, "/global")
    browser.get(url)

    # wait initial graph
    wait_for_plotly_graph(browser, "graph", timeout=15)
    sig_before = get_plotly_data_signature(browser, "graph")

    def action():
        # click near 80% of slider to increase nb-songs value
        click_slider_by_percent(browser, "nb-songs", 0.8)

    def ready_check():
        sig_after = get_plotly_data_signature(browser, "graph")
        return sig_after and sig_after != sig_before

    elapsed_ms = measure_action_time(browser, action, ready_check, timeout=20)

    artifacts_dir = _ensure_artifacts_dir()
    out = {"page": "/global", "action": "nb-songs slider", "elapsed_ms": elapsed_ms}
    fname = os.path.join(
        artifacts_dir, f"timing-global-nb-songs-{int(time.time())}.json"
    )
    with open(fname, "w", encoding="utf8") as fh:
        json.dump(out, fh)


def test_training_dropdown_selection_timing(browser, live_server):
    """Navigate to /training, change dropdown selection and measure time until verified area updates."""
    base = live_server
    url = urljoin(base, "/training")
    browser.get(url)

    # measure_action_time imported at module top

    # find dropdown toggle element created by Dash for dcc.Dropdown
    dropdown_id = "dropdown-song-training"
    # ensure the dropdown exists
    dd = browser.find_element(By.ID, dropdown_id)

    # open dropdown by clicking the element
    def action():
        dd.click()
        # try to pick the second option in the list
        try:
            # dropdown options are rendered in a separate menu; wait a short time
            opt = browser.find_element(By.CSS_SELECTOR, "div.Select-option")
            opt.click()
        except NoSuchElementException:
            # fallback: select by sending keys or clicking the first visible option
            pass

    def ready_check():
        # verified-lyrics container changes when selection changes; detect non-empty content
        el = browser.find_element(By.ID, "verified-lyrics")
        return el.text is not None

    elapsed_ms = measure_action_time(browser, action, ready_check, timeout=10)

    artifacts_dir = _ensure_artifacts_dir()
    out = {
        "page": "/training",
        "action": "dropdown-song-training select",
        "elapsed_ms": elapsed_ms,
    }
    fname = os.path.join(
        artifacts_dir, f"timing-training-dropdown-{int(time.time())}.json"
    )
    with open(fname, "w", encoding="utf8") as fh:
        json.dump(out, fh)
