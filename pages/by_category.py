"""Statistics page for category specific stats."""

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Input, Output, callback, ctx, dcc, html

from pages.utils import (
    compare_to_global,
    download_name,
    filter_date,
    filter_top_songs,
    get_ancienne_formule_options,
    get_category_options,
    get_date_range_object,
    get_download_content_from_store,
    get_mots_options,
    get_nb_songs_slider,
    get_points_options,
)

dash.register_page(__name__, path="/category", title="Par catégorie - NOLPL stats")


layout = dbc.Container(
    [
        html.H4(
            "Chansons les plus populaires par catégorie", style={"marginBottom": 10}
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            options=get_category_options(),
                            value="Points",
                            id="category-selector",
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            options=get_points_options(),
                            value=[50, 40, 30, 20, 10],
                            id="points-selector",
                            multi=True,
                        )
                    ]
                ),
            ]
        ),
        dcc.Graph(id="sorted-graph"),
        html.Div("Nombre de chansons à afficher"),
        get_nb_songs_slider(),
        get_date_range_object(prefix_component_id="category-"),
        html.Div(
            "Statistiques de couverture des catégories avec la sélection actuelle:",
            style={"marginTop": 20},
        ),
        dcc.Markdown("", id="stats-category"),
        dbc.Button("Télécharger la sélection actuelle", id="btn-category-songs"),
        dcc.Download(id="download-category"),
        dcc.Store(id="store-category-top-songs"),
    ],
    style={"marginTop": 20},
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
    if category == "Ancienne formule":
        return get_ancienne_formule_options(), [250, 500, 1000, 2500]
    if category =="Mots":
        mots_options = get_mots_options()
        return mots_options, mots_options
    # for other categories (Même chanson, Maestro, etc.), no option is available
    return [], None


@callback(
    Output("sorted-graph", "figure"),
    Output("stats-category", "children"),
    Output("store-category-top-songs", "data"),
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
    if category_value in set({"Points", "Ancienne formule", "Mots"}):
        graph2_df = graph2_df[graph2_df["points"].isin(points_selector)]
        graph2_df = graph2_df.groupby(by=["name", "points"], as_index=False)[
            "date"
        ].count()
        # get only highest songs
        graph2_df = filter_top_songs(graph2_df, nb_songs)
        to_store = graph2_df.to_csv(index=False, sep=";")
        fig2 = px.histogram(data_frame=graph2_df, x="name", y="date", color="points")
    else:
        graph2_df = graph2_df.groupby(by=["name"], as_index=False)["date"].count()
        graph2_df = filter_top_songs(graph2_df, nb_songs)
        to_store = graph2_df.to_csv(index=False, sep=";")
        fig2 = px.histogram(data_frame=graph2_df, x="name", y="date")
    list_songs = graph2_df["name"].to_list()
    out_child = compare_to_global(date_range, list_songs)
    fig2.update_layout(height=500, xaxis={"categoryorder": "total descending", "title": "Chanson"},
                       yaxis={"title": "Nombre d'apparitions"})
    return fig2, out_child, to_store


@callback(
    Output("download-category", "data"),
    Input("btn-category-songs", "n_clicks"),
    Input("store-category-top-songs", "data"),
    Input("nb-songs", "value"),
    Input("category-year_slider", "value"),
    Input("category-selector", "value"),
    Input("points-selector", "value"),
    prevent_initial_call=True,
)
def download_songs_list(
    _: int,
    data_stored: str,
    nb_songs: int,
    date_range: list[int],
    category: str,
    points_selector: list[int],
):
    # pylint: disable=useless-type-doc, useless-param-doc
    """Download function to save top songs

    Args:
        _ (int): nb of clicks
        data_stored (str): content of dcc.Store (Dataframe)
        nb_songs (int): number of songs
        date_range (list(int)): begin and end date
        category (str): songs category
        points_selector (list[int]): points categories selected

    Returns:
        dict: downloaded content
    """
    if ctx.triggered_id == "btn-category-songs":
        export_df = get_download_content_from_store(data_stored)
        file_category_name = (
            f"{category}-{'_'.join(str(x) for x in points_selector)}"
            if category == "Points"
            else category
        )
        filename = download_name(file_category_name, nb_songs, date_range)
        return {
            "content": export_df.to_csv(),
            "filename": filename,
        }
    return None
