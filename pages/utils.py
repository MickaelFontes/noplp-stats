"""Common utilities functions for all pages."""
import datetime
import time

from dash import dcc, html
import pandas as pd


df = pd.read_csv("data/db_test_full.csv", index_col=None)
df["date"] = pd.to_datetime(df["date"])
df["singer"] = df["singer"].astype("str")
df["name"] = df["name"].astype("str")

daterange = pd.date_range(
    start=df["date"].min().date(),
    end=df["date"].max().date() + datetime.timedelta(days=31),
    freq="MS",
)

daterange_marks = pd.date_range(
    start=df["date"].min().date(), end=df["date"].max().date(), freq="AS"
)


def datetime_to_unix(datetime_instance):
    """Convert datetime to unix timestamp"""
    return int(time.mktime(datetime_instance.timetuple()))


def unix_to_datetime(unix):
    """Convert unix timestamp to datetime."""
    return pd.to_datetime(unix, unit="s")


def get_marks():
    """Returns the marks for labeling.
    Every Nth value will be used.
    """
    result = {}
    for date in daterange_marks:
        result[datetime_to_unix(date)] = str(date.strftime("%Y"))
    return result


def filter_date(date_range):
    """Return a complete songs Dataframe for the data_range argument

    Args:
        date_range (list[int]): date range in Unix format

    Returns:
        Dataframe: songs Dataframe of input data_range
    """
    small, big = date_range
    graph_df = df[df["date"] <= unix_to_datetime(big)]  # type: ignore
    graph_df = graph_df[graph_df["date"] >= unix_to_datetime(small)]
    return graph_df


def filter_date_totals(date_range):
    """Return a complete songs Dataframe for the data_range argument.
    No individuals values by totals by each category.

    Args:
        date_range (list[int]): date range in Unix format

    Returns:
        Dataframe: songs Dataframe of input data_range
    """
    graph_df = filter_date(date_range)
    graph_df = graph_df.groupby(
        by=["category", "points", "date", "emissions"], as_index=False
    ).count()
    graph_df = graph_df.drop(["name", "singer"], axis=1)
    graph_df["to_count"] = 0
    graph_df = graph_df.drop_duplicates()
    return graph_df


def get_time_limits():
    """Return the time limits of full songs Dataframe.

    Returns:
        list[Unix]: [begin, end] in Unix format
    """
    begin = datetime_to_unix(df["date"].min().date().replace(day=1))
    end = datetime_to_unix(df["date"].max().date() + datetime.timedelta(days=31))
    return begin, end


def get_category_options():
    """Return all categories of full songs Dataframe.

    Returns:
        ndarray: unique values of category
    """
    return df["category"].unique()


def get_points_options():
    """Return points options of full songs Dataframe.

    Returns:
        list[int]: list of existing points categories
    """
    return sorted(filter(lambda x: x < 100, df["points"].unique()))[1:]


def get_ancienne_formule_options():
    """Return ancienne formule options of full songs Dataframe.

    Returns:
        list[int]: list of existing ancienne formule gains
    """
    return sorted(filter(lambda x: x > 100, df["points"].unique()))


def get_date_range_object(prefix_component_id=""):
    """Returns layout objects to add a data_range slider.

    Args:
        prefix_component_id (str, optional): prefix string for component names. Defaults to "".

    Returns:
        html.Div: layout component with a date slider
    """
    begin, end = get_time_limits()
    return html.Div(
        [
            html.Label(
                "From 2008 to 2023", id=prefix_component_id + "time-range-label"
            ),
            dcc.RangeSlider(
                id=prefix_component_id + "year_slider",
                min=begin,
                max=end,
                value=[begin, end],
                marks=get_marks(),
            ),
        ],
        style={"margin-top": "20"},
    )


def get_songs():
    """Return all songs names of full songs Dataframe.

    Returns:
        ndarray: unique values of songs name
    """
    return df["name"].unique()


def filter_song(song_name):
    """Return full songs Dataframe for selected song.
    No date_range restriction is applied.

    Returns:
        Dataframe: all rows about the selected song
    """
    return df[df["name"] == song_name]


def get_singers():
    """Return all singers names of full songs Dataframe.

    Returns:
        ndarray: unique values of singers name
    """
    return df["singer"].unique()


def filter_singer(singer_name):
    """Return full songs Dataframe for selected singer.
    No date_range restriction is applied.

    Returns:
        Dataframe: all rows about the selected singer
    """
    return df[df["singer"] == singer_name]


def filter_top_songs(songs_df, nb_songs):
    """Return subset Dataframe wit only the most viewed songs.

    Args:
        songs_df (Dataframe): a songs Dataframe
        nb_songs (int): number of top songs to return

    Returns:
        Dataframe: Dataframe with only the top songs
    """
    filter_top = (
        songs_df.groupby(by=["name"])["date"]
        .sum()
        .sort_values(ascending=False)
        .head(nb_songs)
    )
    songs_df = songs_df[songs_df["name"].isin(filter_top.index.to_list())]
    return songs_df


def compare_to_global(date_range, list_songs):
    """Compute global coverage of provided songs, for the provided date_range.

    Args:
        date_range (list[int]): begin, end of the timeframe
        list_songs (list[str]): list of songs for which coverage is computed

    Returns:
        str: list of song with coverage scores, in Markdown
    """
    table_totals = filter_date_totals(date_range)
    table_individual_songs = filter_date(date_range)
    table_individual_songs = table_individual_songs[
        table_individual_songs["name"].isin(list_songs)
    ]
    table_individual_songs = table_individual_songs.drop(["name", "singer"], axis=1)
    table_individual_songs = table_individual_songs.groupby(
        by=["category", "points", "date", "emissions"], as_index=False
    ).count()
    table_individual_songs["present"] = 1
    table_individual_songs = table_individual_songs.drop_duplicates()
    table_totals = (
        table_totals.merge(
            table_individual_songs,
            left_on=["category", "points", "date", "emissions"],
            right_on=["category", "points", "date", "emissions"],
            how="left",
        )
        .fillna(0)
        .groupby(by=["category", "points"], as_index=False)
        .agg({"to_count": "count", "present": "sum"})
    )
    table_totals["percent"] = table_totals["present"] / table_totals["to_count"]
    table_totals = table_totals[
        table_totals["points"].isin([10, 20, 30, 40, 50])
        | table_totals["category"].isin(["Même chanson", "Maestro"])
    ]
    table_totals = table_totals.fillna(value=0)
    string_d = ""
    for row in table_totals.itertuples():
        display = f" {row.points}" if row.points != -1 else ""
        string_d += f"* {row.category}{display}: {row.percent*100:.1f}%\n"
    return string_d
