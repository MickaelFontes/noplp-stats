"""Statistics page for song specific stats."""
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from pages.utils import (
    extract_and_format_lyrics,
    filter_date,
    filter_song,
    find_singer,
    get_date_range_object,
    get_song_dropdown_menu,
    return_cat_rankings_df,
    return_global_ranking_df,
    return_lyrics_df,
)

dash.register_page(__name__, path="/song", title="Par chanson - NOLPL stats")

first_card = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Sélectionner le titre de la chanson", className="card-title"),
            get_song_dropdown_menu(),
            html.Hr(),
            html.Div(id="song-details"),
        ]
    )
)


layout = dbc.Container(
    [
        html.H4("Statistiques sur la chanson sélectionnée"),
        dbc.Row(
            [
                dbc.Col(first_card, lg=6, xs=0),
                dbc.Col(dcc.Graph(id="categories-graph-song"), lg=6, xs=0),
            ],
            align="center",
            justify="center",
            style={"height": "100%"},
        ),
        get_date_range_object(),
        html.Hr(),
        html.H4("Apparitions de la chanson sur l'émission"),
        dcc.Graph(id="timeline-graph-song"),
        html.Hr(),
        html.H4("Paroles"),
        html.Div(id="song-lyrics", style={"textAlign": "center"}),
    ],
    style={"marginTop": 20},
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
    fig = px.scatter(
        graph_df,
        x=graph_df["date"],
        y=graph_df["category"],
        color=graph_df["category"],
        hover_data={"date": "|%B %d, %Y", "nb": False, "points": True},
    )
    fig.update_layout(showlegend=False)
    return fig


@callback(
    Output("song-details", "children"),
    Output("song-lyrics", "children"),
    Input("dropdown-song", "value"),
)
def update_song_details(song_title: str) -> tuple[list[html.P], list[html.P]]:
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

    lyrics_df = return_lyrics_df()
    lyrics = extract_and_format_lyrics(
        lyrics_df[lyrics_df["name"] == song_title]["lyrics"].values[0]
    )

    return [
        html.P(["Interprète: " + singer, dcc.Markdown(id="singer-field")]),
        html.P("Classement global: " + str(global_rank), id="global-rank"),
        html.P(
            "Classement Même chanson: " + str(meme_chanson_rank), id="meme-chanson-rank"
        ),
        html.P("Classement 50 Points: " + str(fifty_points_rank), id="50-points-rank"),
        html.P("Classement Maestro: " + str(maestro_rank), id="maestro-rank"),
    ], lyrics
