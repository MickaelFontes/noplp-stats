import logging
import re
from urllib.parse import urljoin

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.conftest import (
    get_dropdown_value,
    get_slider_value,
    measure_until_dash_ready,
    record_timing_result,
    wait_for_element,
)

logger = logging.getLogger(__name__)


def _click_nb_songs_target(browser, target_value: int) -> None:
    # Scope DOM queries to the slider container to avoid hitting other sliders on the page
    slider = browser.find_element(By.ID, "nb-songs")
    browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider)
    WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.ID, "nb-songs"))
    )

    mark = slider.find_elements(
        By.XPATH,
        (
            ".//span[contains(@class, 'rc-slider-mark-text') and "
            f"normalize-space()='{target_value}']"
        ),
    )
    if mark:
        mark_element = mark[0]
        mark_style = mark_element.get_attribute("style") or ""
        if left_match := re.search(r"left:\s*([^;]+)", mark_style):
            left_value = left_match.group(1)
            dot = slider.find_elements(
                By.XPATH,
                (
                    f".//span[contains(@class, 'rc-slider-dot') and contains(@style, 'left: {left_value}')]"
                ),
            )
            if dot:
                dot_element = dot[0]
                # Wait for it to be clickable
                WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f".//span[contains(@class, 'rc-slider-dot') and contains(@style, 'left: {left_value}')]",
                        )
                    )
                )
                dot_element.click()
                return

    raise NoSuchElementException(
        f"Could not find slider mark or dot to click for target value {target_value}"
    )


def test_global_nb_songs_slider_updates_and_timing(browser, live_server, request):
    """Navigate to /global, measure initial load, then click slider through multiple values."""
    url = urljoin(live_server, "/global")

    initial_load_ms = measure_until_dash_ready(
        browser, lambda: browser.get(url), timeout=25
    )
    if not initial_load_ms:
        raise TimeoutException("Timed out waiting for /global to become Dash-ready")

    logger.info(
        "[timing] page=%s target=initial_load measured_ms=%s",
        "/global",
        initial_load_ms,
    )

    initial_value = get_slider_value(browser, "nb-songs")
    target_values = [50, 100, 300, 500, 1000, 3000]

    interaction_timings = []

    for target_value in target_values:
        value_before = get_slider_value(browser, "nb-songs")
        elapsed_ms = measure_until_dash_ready(
            browser,
            lambda target_value=target_value: _click_nb_songs_target(
                browser, target_value
            ),
            timeout=25,
        )
        if not elapsed_ms:
            raise TimeoutException(
                f"Timed out waiting for /global to become Dash-ready after nb-songs={target_value}"
            )

        value_after = get_slider_value(browser, "nb-songs")

        interaction_timings.append(
            {
                "target_value": target_value,
                "value_before": value_before,
                "value_after": value_after,
                "value_changed": value_after != value_before,
                "interaction_render_time_ms": elapsed_ms,
            }
        )

        logger.info(
            "[timing] page=%s target_value=%s measured_ms=%s value_before=%s value_after=%s",
            "/global",
            target_value,
            elapsed_ms,
            value_before,
            value_after,
        )

    timings_summary = {"initial_load_ms": initial_load_ms}
    for timing in interaction_timings:
        timings_summary[f"value_{timing['target_value']}_ms"] = timing[
            "interaction_render_time_ms"
        ]

    record_timing_result(
        request,
        {
            "page": "/global",
            "initial_page_load_ms": initial_load_ms,
            "initial_value": initial_value,
            "slider_id": "nb-songs",
            "action": "slider position changes through multiple values: 50, 100, 300, 500, 1000",
            "timings_summary": timings_summary,
            "interaction_timings": interaction_timings,
        },
    )


def test_song_dropdown_selection_timing(browser, live_server, request):
    """Navigate to /song, measure initial load, type a song name in dropdown and measure render time."""
    url = urljoin(live_server, "/song")

    initial_load_ms = measure_until_dash_ready(
        browser, lambda: browser.get(url), timeout=25
    )
    if not initial_load_ms:
        raise TimeoutException("Timed out waiting for /song to become Dash-ready")

    logger.info(
        "[timing] page=%s target=initial_load measured_ms=%s",
        "/song",
        initial_load_ms,
    )

    dropdown_id = "dropdown-song-by-song"
    dd_control = wait_for_element(browser, By.ID, dropdown_id, timeout=15)
    dd_focusable = wait_for_element(
        browser,
        By.CSS_SELECTOR,
        f"#{dropdown_id} input, #{dropdown_id} [role='combobox']",
        timeout=15,
    )

    value_before = get_dropdown_value(browser, dropdown_id)
    song_to_select = "Pour que tu m'aimes encore (Céline Dion)"

    def action():
        browser.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", dd_control
        )
        WebDriverWait(browser, 5).until(EC.visibility_of(dd_focusable))
        browser.execute_script("arguments[0].focus();", dd_focusable)
        dd_focusable.send_keys(song_to_select)
        dd_focusable.send_keys(Keys.ENTER)

    if not (elapsed_ms := measure_until_dash_ready(browser, action, timeout=25)):
        raise TimeoutException(
            f"Timed out waiting for /song to become Dash-ready after selecting dropdown value {song_to_select!r}"
        )

    value_after = get_dropdown_value(browser, dropdown_id)
    value_changed = value_after != value_before

    logger.info(
        "[timing] page=%s target_value=%s measured_ms=%s value_before=%s value_after=%s",
        "/song",
        song_to_select,
        elapsed_ms,
        value_before,
        value_after,
    )

    record_timing_result(
        request,
        {
            "page": "/song",
            "initial_page_load_ms": initial_load_ms,
            "dropdown_id": dropdown_id,
            "value_before": value_before,
            "value_after": value_after,
            "text_after": browser.find_element(By.ID, "song-lyrics").text,
            "value_changed": value_changed,
            "action": f"dropdown selection change - typed '{song_to_select}'",
            "interaction_render_time_ms": elapsed_ms,
        },
    )
