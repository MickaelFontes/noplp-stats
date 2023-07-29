"""Statistics page for song specific stats."""
from functools import reduce

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from pages.utils import (
    filter_date,
    filter_song,
    find_singer,
    get_date_range_object,
    get_songs,
    return_cat_rankings_df,
    return_global_ranking_df,
)

dash.register_page(__name__, path="/song")

lyrics_df = pd.read_csv("data/db_lyrics.csv")

first_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Statistics about one song", className="card-title"),
            html.P("Sélectionner le titre de la chanson"),
            dcc.Dropdown(
                id="dropdown-song",
                value="2 be 3",
                options=[{"label": i, "value": i} for i in get_songs()],
            ),
            html.Hr(),
            html.Div(id="song-details"),
        ]
    )
)


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(first_card),
                dbc.Col(dcc.Graph(id="categories-graph-song")),
            ]
        ),
        get_date_range_object(),
        html.H4("Song occurence in time"),
        dcc.Graph(id="timeline-graph-song"),
        html.Hr(),
        html.Div(
            [
                html.H4("Lyrics"),
                html.Div(id="song-lyrics"),
            ], style={"textAlign": "center"}
        ),
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


@callback(
    Output("song-details", "children"),
    Output("song-lyrics", "children"),
    Input("dropdown-song", "value"),
)
def update_song_details(song_title: str) -> list[html.P]:
    """Query and return song details.

    Args:
        song_title (str): song title

    Returns:
        list[html.P]: Dash elements with the details
    """
    global_df = return_global_ranking_df()
    global_df = global_df[global_df["name"] == song_title]
    singer = find_singer(song_title)
    global_rank = global_df["rank"].values[0]
    cats_df = return_cat_rankings_df()
    cats_df = cats_df[cats_df["name"] == song_title]

    meme_chanson_rank = (
        cats_df[cats_df["category"] == "Même chanson"]["rank"].values[0]
        if not cats_df[cats_df["category"] == "Même chanson"].empty
        else "NA"
    )
    fifty_points_rank = (
        cats_df[cats_df["category"] == "50 Points"]["rank"].values[0]
        if not cats_df[cats_df["category"] == "50 Points"].empty
        else "NA"
    )

    maestro_rank = (
        cats_df[cats_df["category"] == "Maestro"]["rank"].values[0]
        if not cats_df[cats_df["category"] == "Maestro"].empty
        else "NA"
    )

    lyrics = []
    for text_paragraph in (
        lyrics_df[lyrics_df["name"] == song_title]["lyrics"].values[0].split("\\n\\n")
    ):
        text_with_breaks = ([t] for t in text_paragraph.split("\\n"))
        paragraph = html.P(
            list(reduce(lambda a, b: a + [html.Br()] + b, text_with_breaks))
        )
        lyrics.append(paragraph)

    return [
        html.P(["Interprète: " + singer, dcc.Markdown(id="singer-field")]),
        html.P("Classement global: " + str(global_rank), id="global-rank"),
        html.P(
            "Classement Même chanson: " + str(meme_chanson_rank), id="meme-chanson-rank"
        ),
        html.P("Classement 50 Points: " + str(fifty_points_rank), id="50-points-rank"),
        html.P("Classement Maestro: " + str(maestro_rank), id="maestro-rank"),
    ], lyrics
