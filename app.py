"""Application file for noplp-stats"""
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "NOPLP stats - Statistics of occurences on NOPLP"


app.layout = html.Div(
    [
        dbc.NavbarSimple(
            children=[
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Global", href="/global", active="exact"),
                dbc.NavLink("Category", href="/category", active="exact"),
                dbc.NavLink("Song", href="/song", active="exact"),
                dbc.NavLink("Singer", href="/singer", active="exact"),
                dbc.NavLink("Training", href="/training", active="exact"),
            ],
            brand="NOPLP Stats",
            color="primary",
            dark=True,
        ),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run(port="8080", debug=False)
