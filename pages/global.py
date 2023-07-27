"""Global statistics page layout.

Layout of the global statistics page, with graphs callbacks
and some data manipulation.
"""
import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, ctx, dcc, html

from pages.utils import (
    compare_to_global,
    filter_date,
    filter_top_songs,
    get_date_range_object,
    return_coverage_figure,
)

dash.register_page(__name__, path="/global")


layout = html.Div(
    [
        html.H4("Most popular songs of NOPLP"),
        dcc.Graph(id="graph"),
        html.Div("Number of top songs to display"),
        dcc.Slider(
            min=5,
            max=1000,
            step=10,
            value=10,
            marks={i: f"{i}" for i in [5, 10, 50, 100, 300, 500, 1000]},
            id="nb-songs",
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        get_date_range_object(prefix_component_id="global-"),
        html.Div(
            "Coverage stats of the selected date range by the sogs present in the graph:"
        ),
        dcc.Markdown("rien", id="stats-global"),
        html.Button("Download the displayed top songs", id="btn-global-songs"),
        dcc.Download(id="download-global"),
        html.H4("Coverage of categories by number of songs"),
        dcc.Graph(id="coverage-graph", figure=return_coverage_figure()),
        dcc.Store(id="store-global-top-songs"),
    ],
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
    """Download function to save top songs

    Args:
        _ (int): nb of clicks
        data_stored (str): content of dcc.Store (Dataframe)

    Returns:
        dict: downloaded content
    """
    if ctx.triggered_id == "btn-global-songs":
        export_df = pd.DataFrame(
            [row.split(";") for row in data_stored.split("\n")][1:-1],
            columns=list(data_stored.split("\n")[0].split(";")),
        )
        export_df = export_df.astype({"name": "str", "date": "int"})
        export_df = export_df.groupby(by=["name"], as_index=False)["date"].sum()
        export_df.rename({"date": "nb_occurences"}, inplace=True, axis="columns")
        export_df.sort_values(
            by="nb_occurences", ascending=False, inplace=True, ignore_index=True
        )
        export_df.index += 1
        return {"content": export_df.to_csv(), "filename": "global-top-songs-NOPLP.csv"}
    return None
