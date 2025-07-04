"""Application file for noplp-stats"""

import os

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

from pages.bottom import bottom

app = Dash(
    __name__,
    use_pages=True,
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
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Accueil", href="/", active="exact"),
                dbc.NavLink("Global", href="/global", active="exact"),
                dbc.NavLink("Par catégorie", href="/category", active="exact"),
                dbc.NavLink("Par chanson", href="/song", active="partial"),
                dbc.NavLink("Par interprète", href="/singer", active="partial"),
                dbc.NavLink("Entraînement", href="/training", active="exact"),
            ],
            brand="NOPLP Stats",
            color="primary",
            dark=True,
        ),
        dash.page_container,
        html.Div(id="blank-output"),
        bottom,
    ]
)

if __name__ == "__main__":
    app.run(port="8080", debug=None)
