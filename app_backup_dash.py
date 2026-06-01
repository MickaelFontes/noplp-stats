"""Application file for noplp-stats - Flask with embedded Dash apps"""

import os
from flask import Flask
import dash
import dash_bootstrap_components as dbc
from dash import html, Output, Input, State, dcc
from pages.bottom import bottom

# Create Flask app
server = Flask(__name__, static_folder="pages/assets")
server.config["SUPPRESS_CALLBACK_EXCEPTIONS"] = True

# Create main Dash app that wraps with navbar and footer
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        {
            "href": dbc.themes.BOOTSTRAP,
            "rel": "stylesheet",
            "integrity": "sha256-oxqX0LQclbvrsJt8IymkxnISn4Np2Wy2rY9jjoQlDEg=",
            "crossorigin": "anonymous",
        }
    ],
    title="NOPLP stats - Statistiques N'oubliez pas les paroles",
    update_title=None,
)

app.title = "NOPLP stats - Statistiques N'oubliez pas les paroles"
app._base_url = "https://noplp-stats.fr"
# To still have debug control, behind gunicorn, using DASH_DEBUG environment variable.
app.enable_dev_tools(debug=bool(os.getenv("DASH_DEBUG", None)))

# Navbar component
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("NOPLP Stats", href="/"),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavLink(
                            "Accueil",
                            href="/",
                            active="exact",
                            id="nav-accueil",
                        ),
                        dbc.NavLink(
                            "Global",
                            href="/global",
                            active="exact",
                            id="nav-global",
                        ),
                        dbc.NavLink(
                            "Par catégorie",
                            href="/category",
                            active="exact",
                            id="nav-category",
                        ),
                        dbc.NavLink(
                            "Par chanson",
                            href="/song",
                            active="partial",
                            id="nav-song",
                        ),
                        dbc.NavLink(
                            "Par interprète",
                            href="/singer",
                            active="partial",
                            id="nav-singer",
                        ),
                        dbc.NavLink(
                            "Entraînement",
                            href="/training",
                            active="exact",
                            id="nav-training",
                        ),
                    ],
                    className="ml-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="primary",
    dark=True,
)

# Main layout - navbar + page content + footer
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        navbar,
        html.Div(id="page-content", style={"minHeight": "calc(100vh - 200px)"}),
        html.Div(id="blank-output"),
        bottom,
    ]
)


# Callback to route to different pages
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    """Route pages based on URL pathname"""
    if pathname == "/" or pathname == "":
        from pages.home import get_home_layout
        return get_home_layout()
    elif pathname == "/global":
        return html.Div("Global page - coming soon")
    elif pathname == "/category":
        return html.Div("Category page - coming soon")
    elif pathname == "/song":
        return html.Div("Song page - coming soon")
    elif pathname == "/singer":
        return html.Div("Singer page - coming soon")
    elif pathname == "/training":
        return html.Div("Training page - coming soon")
    else:
        return html.Div("Page not found", style={"padding": "20px"})


# Callback to toggle/collapse navbar on toggler click or navlink click
@app.callback(
    Output("navbar-collapse", "is_open"),
    [
        Input("navbar-toggler", "n_clicks"),
        Input("nav-accueil", "n_clicks"),
        Input("nav-global", "n_clicks"),
        Input("nav-category", "n_clicks"),
        Input("nav-song", "n_clicks"),
        Input("nav-singer", "n_clicks"),
        Input("nav-training", "n_clicks"),
    ],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar(
    _n_toggler,
    _n_accueil,
    _n_global,
    _n_category,
    _n_song,
    _n_singer,
    _n_training,
    is_open,
):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open
    if ctx.triggered[0]["prop_id"].split(".")[0] == "navbar-toggler":
        return not is_open
    # If any navlink is clicked, close the navbar (only matters on mobile)
    return False


if __name__ == "__main__":
    app.run(port="8080", debug=None)
