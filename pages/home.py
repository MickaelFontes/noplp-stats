"""Home page layout."""
import dash
import dash_bootstrap_components as dbc
from dash import html

dash.register_page(__name__, path="/")

layout = dbc.Container(
    children=[
        html.H1(children="This is our Home page"),
        html.Div(
            children="""
        This is our Home page content.
    """
        ),
    ]
)
