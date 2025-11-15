"""Application file for noplp-stats"""

import os

import dash
import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, State, html

from pages.bottom import bottom

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    update_title="",
    assets_folder="pages/assets",
)
server = app.server
app.title = "NOPLP stats - Statistiques sur N'oubliez pas les paroles"
# To still have debug control, behind gunicorn, using DASH_DEBUG environment variable.
app.enable_dev_tools(debug=bool(os.getenv("DASH_DEBUG", None)))

app.layout = html.Div(
    [
        dbc.Navbar(
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
        ),
        dash.page_container,
        html.Div(id="blank-output"),
        bottom,
    ]
)


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
