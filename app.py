"""Application file for noplp-stats"""
from dash import Dash, dcc, html
import dash

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)
server = app.server
app.title = "NOPLP stats - Statistics of occurences on NOPLP"


app.layout = html.Div(
    [
        html.H1("NOLPL stats - Search, learn, sing."),
        html.Div(
            [
                html.Div(
                    dcc.Link(
                        f"{page['name']} - {page['path']}", href=page["relative_path"]
                    )
                )
                for page in dash.page_registry.values()
            ]
        ),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run_server(port=8080, debug=None)
