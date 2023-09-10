"""Home page layout."""
import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, path="/", title="NOLPL stats")

homepage_markdown = """# 
"""

layout = dbc.Container(
    children=[
        html.H1(children=homepage_markdown),
    ],
    style={"marginTop": 20},
)
