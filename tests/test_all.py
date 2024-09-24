from dash.testing.composite import DashComposite

from app import app as noplp_app


def test_all_pages(dash_duo: DashComposite):
    # 4. host the app locally in a thread, all dash server configs could be
    # passed after the first app argument
    dash_duo.start_server(noplp_app)
    # 5. use wait_for_* if your target element is the result of a callback,
    # keep in mind even the initial rendering can trigger callbacks
    print(dash_duo.server_url)
    dash_duo.wait_for_page()
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    dash_duo.wait_for_page(dash_duo.server_url + "/global")
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    dash_duo.wait_for_page(dash_duo.server_url + "/category")
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    # dash_duo.wait_for_page(dash_duo.server_url + "/song")
    # assert dash_duo.get_logs() == [], "browser console should contain no error"
    dash_duo.wait_for_page(dash_duo.server_url + "/singer")
    assert dash_duo.get_logs() == [], "browser console should contain no error"
    dash_duo.wait_for_page(dash_duo.server_url + "/training")
    assert dash_duo.get_logs() == [], "browser console should contain no error"
