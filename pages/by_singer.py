"""Statistics page for singer specific stats."""
from urllib.parse import unquote

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from pages.utils import filter_date, filter_singer, get_date_range_object, get_singers

dash.register_page(__name__, path="/singer", path_template="/singer/<singer_name>",
                   title="Par interprète - NOLPL stats")


def layout(singer_name="Celine Dion"):
    return dbc.Container(
        [
            dcc.Location(id="url-singer", refresh=False),
            html.H4(
                "Statistiques sur les chansons d'un.e interprète",
                style={"marginBottom": 10},
            ),
            dcc.Dropdown(
                id="dropdown-singer",
                value=singer_name,
                options=[{"label": i, "value": i} for i in get_singers()],
                style={"marginBottom": 10},
            ),
            get_date_range_object(),
            dcc.Graph(id="categories-graph-singer"),
            html.Hr(),
            html.H4("Apparitions de ses chansons dans l'émission"),
            dcc.Graph(id="timeline-graph-singer"),
        ],
        style={"marginTop": 20},
    )


@callback(
    Output("url-singer", "pathname"),
    Input("dropdown-singer", "value"),
    Input("url-singer", "pathname"),
)
def update_url_from_dropdown_singer(singer_name, url_pathname):
    len_singer_prefix = len("/singer")
    if url_pathname[:len_singer_prefix] == "/singer":
        if unquote(url_pathname)[len_singer_prefix+1:] == singer_name:
            return dash.no_update
        singer_url = f"/singer/{singer_name}"
        return singer_url
    return dash.no_update


@callback(
    Output("categories-graph-singer", "figure"),
    Input("dropdown-singer", "value"),
    Input("year_slider", "value"),
)
def update_figure(song_name, date_range):
    """Update the graph with the singer's songs stats.

    Args:
        song_name (str): Song title.
        date_range (int): date range in Unix format.

    Returns:
        figure: songs graph for selected singer.
    """
    graph_df = filter_date(date_range)
    graph_df = graph_df[graph_df["singer"] == song_name]
    graph_df = graph_df.astype({"points": "string"})
    graph_df["category"] = graph_df.category + " " + graph_df.points
    graph_df["category"] = graph_df["category"].str.replace(" -1", "")
    graph_df = graph_df.groupby(by=["name", "category"], as_index=False)["date"].count()
    fig = px.histogram(data_frame=graph_df, x="name", y="date", color="category")
    fig.update_layout(height=500, xaxis={"categoryorder": "total descending"})
    return fig


@callback(Output("timeline-graph-singer", "figure"), Input("dropdown-singer", "value"))
def update_timeline(singer_name):
    """Update the timeline graph of the singer

    Args:
        singer_name (str): Singer's name.

    Returns:
        fig: Graph with the songs occurences.
    """
    graph_df = filter_singer(singer_name)
    graph_df.insert(5, "nb", 1)
    # fix view VS copy
    graph_df = graph_df.astype({"points": "string"})
    graph_df["category"] = graph_df.points + " " + graph_df.category
    graph_df["category"] = graph_df["category"].str.replace("-1 ", "")
    fig = px.scatter(
        graph_df,
        x=graph_df["date"],
        y=graph_df["name"],
        color=graph_df["category"],
        hover_data={
            "date": "|%B %d, %Y",
            "nb": False,
            "points": False,
            "category": True,
        },
    )
    fig.update_xaxes(showgrid=True, ticklabelmode="instant", dtick="M12")
    fig.update_layout(
        height=500,
        yaxis={
            "categoryorder": "array",
            "categoryarray": [
                "10 Points",
                "20 Points",
                "30 Points",
                "40 Points",
                "50 Points",
                "Même chanson",
            ],
        },
    )
    return fig
