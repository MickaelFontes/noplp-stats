from dash.testing.application_runners import import_app
from dash.testing.composite import DashComposite


def test_all_pages(dash_duo: DashComposite):
    # 4. host the app locally in a thread, all dash server configs could be
    # passed after the first app argument
    app = import_app("app")
    dash_duo.start_server(app)
    # 5. use wait_for_* if your target element is the result of a callback,
    # keep in mind even the initial rendering can trigger callbacks
    print(dash_duo.server_url)
    dash_duo.wait_for_page()
    dash_duo.wait_for_page(dash_duo.server_url + "/global")
    dash_duo.wait_for_page(dash_duo.server_url + "/category")
    dash_duo.wait_for_page(dash_duo.server_url + "/song")
    dash_duo.wait_for_page(dash_duo.server_url + "/singer")
    dash_duo.wait_for_page(dash_duo.server_url + "/training")
    # acceptance criterion as an assert message after the comma.
    assert dash_duo.get_logs() == [], "browser console should contain no error"
