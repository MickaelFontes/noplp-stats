"""Statistics page for category specific stats."""

import dash
import plotly.express as px
from dash import Input, Output, callback, dcc, html

from pages.utils import (
    compare_to_global,
    filter_date,
    filter_top_songs,
    get_ancienne_formule_options,
    get_category_options,
    get_date_range_object,
    get_points_options,
)

dash.register_page(__name__, path="/category")


layout = html.Div(
    [
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
        get_date_range_object(prefix_component_id="category-"),
        dcc.Markdown("", id="stats-category"),
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
    elif category == "Ancienne formule":
        return get_ancienne_formule_options(), [500, 1000, 2500]
    # for other categories (Même chanson, Maestro, etc.), no option is available
    return [], None

@callback(
    Output("sorted-graph", "figure"),
    Output("stats-category", "children"),
    Input("category-year_slider", "value"),
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
