"""Global statistics page layout.

Layout of the global statistics page, with graphs callbacks
and some data manipulation.
"""

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, ctx, dcc, html

from pages.utils import (
    compare_to_global,
    filter_date,
    filter_top_songs,
    get_date_range_object,
    get_download_content_from_store,
    get_nb_songs_slider,
    return_coverage_figure,
)

dash.register_page(__name__, path="/global", title="Global - NOLPL stats")


layout = dbc.Container(
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


@callback(
    Output("graph", "figure"),
    Output("stats-global", "children"),
    Output("store-global-top-songs", "data"),
    Input("global-year_slider", "value"),
    Input("nb-songs", "value"),
)
def update_figure(date_range, nb_songs):
    """Update global graph ranking.

    Args:
        date_range (list[int]): date range in Unix format
        nb_songs (int): Number of top songs to display

    Returns:
        fig: Top songs graph, accross all categories
    """
    graph_df = filter_date(date_range)
    graph_df = graph_df.groupby(by=["name", "category"], as_index=False)["date"].count()
    graph_df = graph_df.sort_values(by=["date"], ascending=False)
    graph_df = filter_top_songs(graph_df, nb_songs)
    to_store = graph_df.to_csv(index=False, sep=";")
    fig = px.histogram(data_frame=graph_df, x="name", y="date", color="category")
    fig.update_layout(height=500, xaxis={"categoryorder": "total descending"})
    list_songs = graph_df["name"].to_list()
    out_child = compare_to_global(date_range, list_songs)
    return fig, out_child, to_store


@callback(
    Output("download-global", "data"),
    Input("btn-global-songs", "n_clicks"),
    Input("store-global-top-songs", "data"),
    prevent_initial_call=True,
)
def download_songs_list(_, data_stored):
    # pylint: disable=useless-type-doc, useless-param-doc
    """Download function to save top songs

    Args:
        _ (int): nb of clicks
        data_stored (str): content of dcc.Store (Dataframe)

    Returns:
        dict: downloaded content
    """
    if ctx.triggered_id == "btn-global-songs":
        export_df = get_download_content_from_store(data_stored)
        return {"content": export_df.to_csv(), "filename": "global-top-songs-NOPLP.csv"}
    return None
