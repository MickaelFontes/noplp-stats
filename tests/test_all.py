from urllib.parse import urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from app import app as noplp_app


def test_all_pages(browser, live_server):
    routes = [
        ("/", "NOPLP stats - Statistiques N'oubliez pas les paroles"),
        ("/global", "Global - NOPLP stats - Statistiques N'oubliez pas les paroles"),
        (
            "/category",
            "Par catégorie - NOPLP stats - Statistiques N'oubliez pas les paroles",
        ),
        ("/song", "Par chanson - NOPLP stats - Statistiques N'oubliez pas les paroles"),
        (
            "/singer",
            "Par interprète - NOPLP stats - Statistiques N'oubliez pas les paroles",
        ),
        (
            "/training",
            "Entraînement - NOPLP stats - Statistiques N'oubliez pas les paroles",
        ),
    ]

    assert noplp_app.title == "NOPLP stats - Statistiques N'oubliez pas les paroles"

    for path, expected_title in routes:
        browser.get(urljoin(live_server, path))
        WebDriverWait(browser, 10).until(ec.title_is(expected_title))
        assert browser.find_element(By.ID, "navbar-toggler")
