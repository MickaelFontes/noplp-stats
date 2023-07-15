"""Statistics page for song specific stats."""
import dash
from dash import dcc, html, callback, Input, Output
import plotly.express as px

from pages.utils import (
    get_date_range_object,
    get_songs,
    filter_date,
    filter_song,
)

dash.register_page(__name__, path="/song")

layout = html.Div(
    [
        html.H4("Satistics about one song"),
        dcc.Dropdown(
            id="dropdown-song",
            value="2 be 3",
            options=[{"label": i, "value": i} for i in get_songs()],
        ),
        get_date_range_object(),
        dcc.Graph(id="categories-graph-song"),
        html.H4("Song occurence in time"),
        dcc.Graph(id="timeline-graph-song"),
    ]
)


@callback(
    Output("categories-graph-song", "figure"),
    Input("dropdown-song", "value"),
    Input("year_slider", "value"),
)
def update_figure(song_name, date_range):
    """Update the categories graph for selected song.

    Args:
        song_name (str): song title
        date_range (list[int]): data range, in Unix format

    Returns:
        fig: chart graph by value
    """
    graph_df = filter_date(date_range)
    graph_df = graph_df[graph_df["name"] == song_name]
    graph_df = graph_df.groupby(by=["name", "category", "points"], as_index=False)[
        "date"
    ].count()
    fig = px.histogram(data_frame=graph_df, x="category", y="date", color="points")
    fig.update_layout(height=500, xaxis={"categoryorder": "total descending"})
    return fig


@callback(Output("timeline-graph-song", "figure"), Input("dropdown-song", "value"))
def update_timeline(song_name):
    """Update the timeline graph of selected song.

    Args:
        song_name (str): song title

    Returns:
        fig: timeline graph
    """
    graph_df = filter_song(song_name)
    graph_df.insert(5, "nb", 1)
    # fix view VS copy
    graph_df = graph_df.astype({"points": "string"})
    graph_df["category"] = graph_df.category + " " + graph_df.points
    graph_df["category"] = graph_df["category"].str.replace(" -1", "")
    fig = px.bar(
        graph_df,
        x=graph_df["date"],
        y=graph_df["nb"],
        color=graph_df["category"],
        hover_data={"date": "|%B %d, %Y", "nb": False, "points": True},
    )
    return fig
