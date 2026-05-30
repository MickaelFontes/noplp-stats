import logging
from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from app import app as noplp_app
from tests.conftest import measure_until_dash_ready, record_timing_result

logger = logging.getLogger(__name__)


def test_all_pages(browser, live_server, request):
    routes = [
        ("/", "NOPLP stats - Statistiques N'oubliez pas les paroles"),
        ("/global", "Global - NOPLP stats - Statistiques N'oubliez pas les paroles"),
        (
            "/category",
            "Par catégorie - NOPLP stats - Statistiques N'oubliez pas les paroles",
        ),
        (
            "/song/2 be 3",
            "2 be 3 - NOPLP stats - Statistiques N'oubliez pas les paroles",
        ),
        (
            "/singer/Céline Dion",
            "Céline Dion - NOPLP stats - Statistiques N'oubliez pas les paroles",
        ),
        (
            "/training",
            "Entraînement - NOPLP stats - Statistiques N'oubliez pas les paroles",
        ),
    ]

    assert noplp_app.title == "NOPLP stats - Statistiques N'oubliez pas les paroles"

    per_route_timings = []

    for path, expected_title in routes:
        initial_page_load_ms = measure_until_dash_ready(
            browser,
            lambda path=path: browser.get(urljoin(live_server, path)),
            timeout=10,
        )
        if not initial_page_load_ms:
            raise TimeoutError(f"Timed out waiting for {path} to become Dash-ready")

        logger.info(
            "[timing] page=%s target=initial_load measured_ms=%s",
            path,
            initial_page_load_ms,
        )

        WebDriverWait(browser, 10).until(ec.title_is(expected_title))
        assert browser.find_element(By.ID, "navbar-toggler")

        per_route_timings.append(
            {
                "path": path,
                "page_title": expected_title,
                "initial_page_load_ms": initial_page_load_ms,
            }
        )

        # Check browser console for errors (equivalent to dash_duo.get_logs())
        logs = browser.get_log("browser")
        error_logs = [log for log in logs if log["level"] == "SEVERE"]
        assert (
            error_logs == []
        ), f"Browser console should contain no errors on {path}: {error_logs}"

    record_timing_result(
        request,
        {
            "routes_count": len(routes),
            "routes": per_route_timings,
        },
    )
