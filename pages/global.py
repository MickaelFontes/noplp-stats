"""Global statistics page layout.

Layout of the global statistics page, with graphs callbacks
and some data manipulation.
"""
from dash import dcc, html, callback, Input, Output
import dash
import pandas as pd
import plotly.express as px

from pages.utils import (
    get_category_options,
    get_points_options,
    get_date_range_object,
    filter_date,
    filter_top_songs,
    compare_to_global,
)

dash.register_page(__name__, path="/global")


layout = html.Div(
    [
        html.Div(
            [
                html.H4("Number of top songs to display"),
                dcc.Slider(
                    min=5,
                    max=1000,
                    step=10,
                    value=10,
                    marks={i: f"{i}" for i in [5, 10, 50, 100, 300, 1000]},
                    id="nb-songs",
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ]
        ),
        dcc.Markdown("rien", id="stats-global"),
        html.H4("Most popular songs of NOPLP"),
        dcc.Graph(id="graph"),
        get_date_range_object(prefix_component_id="global-"),
        html.H4("Most popular songs by category"),
        html.Div(
            [
                dcc.Dropdown(
                    options=get_category_options(),
                    value="Points",
                    id="category-selector",
                )
            ],
            style={"width": "48%", "display": "inline-block"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    options=get_points_options(),
                    value=[50, 40, 30, 20, 10],
                    id="points-selector",
                    multi=True,
                )
            ],
            style={"width": "48%", "float": "right", "display": "inline-block"},
        ),
        dcc.Graph(id="sorted-graph"),
        dcc.Markdown("", id="stats-category"),
        html.H4("Coverage of categories by number of songs"),
        dcc.Graph(id="coverage-graph"),
        get_date_range_object(prefix_component_id="coverage-"),
    ]
)


@callback(
    Output("points-selector", "options"),
    Output("points-selector", "value"),
    Input("category-selector", "value"),
)
def update_options_category(category):
    """Update available category options.
    Remove options according to selected category.

    Args:
        category (str): song category

    Returns:
        list_options, selected_options: list, list
    """
    if category == "Points":
        return get_points_options(), [50, 40, 30, 20, 10]
    # for other categories (Même chanson, Maestro, etc.), no option is available
    return [], None


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


@callback(
    Output("sorted-graph", "figure"),
    Output("stats-category", "children"),
    Input("global-year_slider", "value"),
    Input("category-selector", "value"),
    Input("points-selector", "value"),
    Input("nb-songs", "value"),
)
def update_figure2(date_range, category_value, points_selector, nb_songs):
    """Update global ranking graph on selected categories.

    Args:
        date_range (list[int]): date range in Unix format
        category_value (str): Selected category
        points_selector (list[int]): Points categories selected (if main category is Points)
        nb_songs (int): Number of top songs to display

    Returns:
        fig: Top songs graph on selected category
    """
    graph2_df = filter_date(date_range)
    graph2_df = graph2_df[graph2_df["category"] == category_value]
    if category_value == "Points":
        graph2_df = graph2_df[graph2_df["points"].isin(points_selector)]
        graph2_df = graph2_df.groupby(by=["name", "points"], as_index=False)[
            "date"
        ].count()
        # get only highest songs
        graph2_df = filter_top_songs(graph2_df, nb_songs)
        fig2 = px.histogram(data_frame=graph2_df, x="name", y="date", color="points")
    else:
        graph2_df = graph2_df.groupby(by=["name"], as_index=False)["date"].count()
        graph2_df = filter_top_songs(graph2_df, nb_songs)
        fig2 = px.histogram(data_frame=graph2_df, x="name", y="date")
    list_songs = graph2_df["name"].to_list()
    out_child = compare_to_global(date_range, list_songs)
    fig2.update_layout(height=500, xaxis={"categoryorder": "total descending"})
    return fig2, out_child


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
