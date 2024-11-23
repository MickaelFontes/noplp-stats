"""Trends in songs or singer popularity in the show."""

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from pages.utils import filter_date, filter_singer, get_date_range_object, get_singers

dash.register_page(__name__, path="/trends", title="Tendances - NOLPL stats")

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, ctx, dcc, html

from pages.utils import (
    compare_to_global,
    filter_date,
    filter_songs,
    filter_top_songs,
    get_ancienne_formule_options,
    get_category_options,
    get_song_dropdown_menu,
    get_date_range_object,
    get_download_content_from_store,
    get_nb_songs_slider,
    get_points_options,
)


layout = dbc.Container(
    [
        html.H4(
            "Chansons les plus tendances", style={"marginBottom": 10}
        ),
        get_song_dropdown_menu(multi=True),
        get_date_range_object(prefix_component_id="trends-songs-"),
        dcc.Graph(id="graph-trends-songs"),
    ],
    style={"marginTop": 20},
)

@callback(
    Output("graph-trends-songs", "figure"),
    Input("trends-songs-year_slider", "value"),
    Input("dropdown-song", "value"),
)
def update_figure_trends_songs(date_range, list_songs):
    """Update global graph ranking.

    Args:
        date_range (list[int]): date range in Unix format

    Returns:
        fig: Top songs graph, accross all categories
    """
    graph_df = filter_songs(list_songs)
    graph_df = filter_date(date_range, graph_df)
    graph_df = graph_df.sort_values(by=["date"], ascending=False)
    graph_df["date"] = pd.to_datetime(graph_df["date"])
    df_count = graph_df.groupby([graph_df["date"].dt.date, "name"]).size().reset_index(name="Occurrences")
    df_count['Cumulative_Occurrences'] = df_count.groupby('name')['Occurrences'].cumsum()
    fig = px.line(data_frame=df_count, x="date", y="Cumulative_Occurrences",color="name")
    fig.update_layout(height=500, xaxis={"categoryorder": "total descending"})
    list_songs = graph_df["name"].to_list()
    return fig
