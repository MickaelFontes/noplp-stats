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
        dcc.Graph(id="coverage-graph"),
        get_date_range_object(prefix_component_id="coverage-"),
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
        x="rank",
        y="coverage",
        color="category",
        hover_data={"name": True, "rank": True, "coverage": True, "category": True},
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
    same_base_df = songs_df[songs_df["category"] == cat]
    # 1: Order songs by descending (after groupby(date, emissions))
    songs_ranking = (
        same_base_df.groupby(by=["name"], as_index=False)[["date"]]
        .count()
        .sort_values(by=["date"], ascending=False)
    )
    songs_ranking.drop_duplicates(inplace=True)
    # 1.1: Calculate denopminator (date, emissions)
    denominator_df = same_base_df.groupby(by=["date", "emissions"], as_index=False)[
        "singer"
    ].count()
    denominator_df.drop_duplicates(inplace=True)
    denominator = len(denominator_df)
    # 2: For each song, merge first selected songs (remove duplicates)
    #    and compute coverage against all other songs
    iter_coverage = []
    selected_songs = []
    for song_name, _ in songs_ranking.itertuples(name=None, index=False):
        selected_songs += [song_name]
        selection_df = same_base_df[same_base_df["name"].isin(selected_songs)]
        numerator = songs_ranking[songs_ranking["name"].isin(selected_songs)][
            "date"
        ].sum()
        selection_df = selection_df.groupby(
            by=["name", "date", "emissions"], as_index=False
        ).count()
        selection_df = selection_df.drop(["name"], axis=1)
        nb_dupli = selection_df.duplicated().astype(int).sum()
        iter_coverage += [(numerator - nb_dupli) / denominator * 100]
    songs_ranking["rank"] = 1
    songs_ranking["rank"] = songs_ranking["rank"].cumsum()
    songs_ranking["category"] = cat.split(" ", 1)[1] if "-1" in cat else cat
    songs_ranking["coverage"] = iter_coverage
    return songs_ranking


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
