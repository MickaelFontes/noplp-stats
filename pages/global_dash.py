"""Global statistics Dash app served from the Flask web site."""

import os

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, ctx, dcc, html

from pages.bootstrap import BOOTSTRAP_CSS, BOOTSTRAP_JS
from pages.utils import (
    compare_to_global,
    download_name,
    filter_date,
    filter_top_songs,
    get_date_range_object,
    get_download_content_from_store,
    get_nb_songs_slider,
    return_coverage_figure,
)


def _build_index_string() -> str:
    """Return a Bootstrap-wrapped Dash index string."""
    return f"""<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand fw-semibold" href="/">NOPLP Stats</a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navContent" aria-controls="navContent" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navContent">
                    <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                        <li class="nav-item"><a class="nav-link" href="/">Accueil</a></li>
                        <li class="nav-item"><a class="nav-link active" href="/global">Global</a></li>
                        <li class="nav-item"><a class="nav-link" href="/category">Catégories</a></li>
                        <li class="nav-item"><a class="nav-link" href="/song">Chansons</a></li>
                        <li class="nav-item"><a class="nav-link" href="/singer">Interprètes</a></li>
                        <li class="nav-item"><a class="nav-link" href="/training">Entraînement</a></li>
                    </ul>
                </div>
            </div>
        </nav>

        <main class="container py-4 py-lg-5">
            <div id="react-entry-point">{{%app_entry%}}</div>
        </main>

        <footer class="border-top bg-white">
            <div class="container py-3 small text-center">
                <span>NOPLP Stats • Données issues du wiki Fandom NOPLP • Open source sur GitHub</span>
            </div>
        </footer>

        <script src="{BOOTSTRAP_JS['src']}" integrity="{BOOTSTRAP_JS['integrity']}" crossorigin="{BOOTSTRAP_JS['crossorigin']}"></script>
        {{%config%}}
        {{%scripts%}}
        {{%renderer%}}
    </body>
</html>"""


def create_global_dash(server=None):
    """Create the global statistics Dash app."""
    global_dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/global/",
        suppress_callback_exceptions=True,
        external_stylesheets=[BOOTSTRAP_CSS],
        title="Global - NOPLP stats - Statistiques N'oubliez pas les paroles",
        update_title=None,
    )
    global_dash_app.index_string = _build_index_string()
    global_dash_app.layout = dbc.Container(
        [
            html.H4("Chansons les plus populaires (toutes catégories confondues)"),
            dcc.Graph(id="graph"),
            html.Div("Nombre de chansons à afficher"),
            get_nb_songs_slider(),
            get_date_range_object(prefix_component_id="global-"),
            html.Div(
                "Statistiques de couverture des catégories avec la sélection actuelle:",
                style={"marginTop": 20},
            ),
            dcc.Markdown("rien", id="stats-global"),
            dbc.Button("Télécharger la sélection actuelle", id="btn-global-songs"),
            dcc.Download(id="download-global"),
            html.Hr(),
            html.H4(
                "Statistiques de couverture des catégories en fonction du nombre de chanson (sur l'ensemble des émissions)"
            ),
            dcc.Graph(id="coverage-graph", figure=return_coverage_figure()),
            dcc.Store(id="store-global-top-songs"),
        ],
        style={"marginTop": 20},
    )

    return global_dash_app


dash_app = create_global_dash(server=False)


@callback(
    Output("graph", "figure"),
    Output("stats-global", "children"),
    Output("store-global-top-songs", "data"),
    Input("global-year_slider", "value"),
    Input("nb-songs", "value"),
)
def update_figure(date_range, nb_songs):
    """Update global graph ranking."""
    graph_df = filter_date(date_range)
    graph_df = graph_df.groupby(by=["name", "category"], as_index=False)["date"].count()
    graph_df = graph_df.sort_values(by=["date"], ascending=False)
    graph_df = filter_top_songs(graph_df, nb_songs)
    to_store = graph_df.to_csv(index=False, sep=";")
    fig = px.histogram(data_frame=graph_df, x="name", y="date", color="category")
    fig.update_layout(
        height=500,
        xaxis={"categoryorder": "total descending", "title": "Chanson"},
        yaxis={"title": "Nombre d'apparitions"},
        legend={"title": {"text": "Catégorie"}},
    )
    list_songs = graph_df["name"].to_list()
    out_child = compare_to_global(date_range, list_songs)
    return fig, out_child, to_store


@callback(
    Output("download-global", "data"),
    Input("btn-global-songs", "n_clicks"),
    Input("store-global-top-songs", "data"),
    Input("nb-songs", "value"),
    Input("global-year_slider", "value"),
    prevent_initial_call=True,
)
def download_songs_list(_, data_stored, nb_songs, date_range):
    # pylint: disable=useless-type-doc, useless-param-doc
    """Download function to save top songs."""
    if ctx.triggered_id == "btn-global-songs":
        export_df = get_download_content_from_store(data_stored)
        filename = download_name("global", nb_songs, date_range)
        return {"content": export_df.to_csv(), "filename": filename}
    return None
