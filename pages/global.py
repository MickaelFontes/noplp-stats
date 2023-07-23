"""Global statistics page layout.

Layout of the global statistics page, with graphs callbacks
and some data manipulation.
"""
import dash
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from pages.utils import (
    compare_to_global,
    filter_date,
    filter_top_songs,
    get_date_range_object,
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
            marks={i: f"{i}" for i in [5, 10, 50, 100, 300, 1000]},
            id="nb-songs",
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        get_date_range_object(prefix_component_id="global-"),
        dcc.Markdown("rien", id="stats-global"),
        html.H4("Coverage of categories by number of songs"),
        dcc.Graph(id="coverage-graph"),
        get_date_range_object(prefix_component_id="coverage-"),
    ]
)


@callback(
    Output("graph", "figure"),
    Output("stats-global", "children"),
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
    fig = px.histogram(data_frame=graph_df, x="name", y="date", color="category")
    fig.update_layout(height=500, xaxis={"categoryorder": "total descending"})
    list_songs = graph_df["name"].to_list()
    out_child = compare_to_global(date_range, list_songs)
    return fig, out_child


@callback(Output("coverage-graph", "figure"), Input("coverage-year_slider", "value"))
def update_coverage_figure(date_range):
    """Update coverage figure.

    Args:
        date_range (list[int]): date range in Unix format

    Returns:
        fig: coverage graph
    """
    graph_df = filter_date(date_range)
    graph_df["category"] = graph_df["points"].astype(str) + " " + graph_df["category"]
    graph_maestro = return_df_cumsum_category(graph_df, "-1 Maestro")
    graph_50 = return_df_cumsum_category(graph_df, "50 Points")
    graph_40 = return_df_cumsum_category(graph_df, "40 Points")
    graph_30 = return_df_cumsum_category(graph_df, "30 Points")
    graph_meme = return_df_cumsum_category(graph_df, "-1 Même chanson")
    graph_all = pd.concat([graph_maestro, graph_50, graph_40, graph_30, graph_meme])
    fig = px.line(
        data_frame=graph_all,
        x="nb",
        y="date",
        color="category",
        hover_data={"name": True, "nb": True, "date": True, "category": True},
    )
    return fig


def return_df_cumsum_category(songs_df, cat):
    """Compute cumulative sum for songs coverage.

    Args:
        songs_df (Dataframe): songs dataframe of selected timeframe
        cat (str): Song category

    Returns:
        Dataframe: Dataframe with "nb" column as cumulative sum
    """
    graph_df = songs_df[songs_df["category"] == cat]
    graph_df = graph_df.groupby(by=["name"], as_index=False)["date"].count()
    graph_df = graph_df.sort_values(ascending=False, by=["date"])
    graph_df["date"] = graph_df["date"].cumsum()
    graph_df["date"] = graph_df["date"] / graph_df["date"].max()
    graph_df["nb"] = 1
    graph_df["nb"] = graph_df["nb"].cumsum()
    graph_df["category"] = cat
    return graph_df
