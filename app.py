"""Application file for noplp-stats"""

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

from pages.bottom import bottom

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    update_title="",
)
server = app.server
app.title = "NOPLP stats - Statistiques sur N'oubliez pas les paroles"


app.layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Accueil", href="/", active="exact"),
                dbc.NavLink("Global", href="/global", active="exact"),
                dbc.NavLink("Par catégorie", href="/category", active="exact"),
                dbc.NavLink("Par chanson", href="/song", active="exact"),
                dbc.NavLink("Par interprète", href="/singer", active="exact"),
                dbc.NavLink("Entraînement", href="/training", active="exact"),
            ],
            brand="NOPLP Stats",
            color="primary",
            dark=True,
        ),
        dash.page_container,
        bottom,
    ]
)

if __name__ == "__main__":
    app.run(port="8080", debug=None)
