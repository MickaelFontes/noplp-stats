"""Common utilities functions for all pages."""
import datetime
import time

from dash import dcc, html
import pandas as pd


df = pd.read_csv("data/db_test_full.csv", index_col=None)
df["date"] = pd.to_datetime(df["date"])

daterange = pd.date_range(
    start=df["date"].min().date(),
    end=df["date"].max().date() + datetime.timedelta(days=31),
    freq="MS",
)

daterange_marks = pd.date_range(
    start=df["date"].min().date(), end=df["date"].max().date(), freq="AS"
)


def datetime_to_unix(dt):
    """Convert datetime to unix timestamp"""
    return int(time.mktime(dt.timetuple()))


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
    small, big = date_range
    graph_df = df[df["date"] <= unix_to_datetime(big)]  # type: ignore
    graph_df = graph_df[graph_df["date"] >= unix_to_datetime(small)]
    return graph_df


def filter_date_totals(date_range):
    graph_df = filter_date(date_range)
    graph_df = graph_df.groupby(by=["category", "points"], as_index=False)[
        "date"
    ].count()
    graph_df = graph_df.rename(columns={"date": "total"})
    return graph_df


def get_time_limits():
    begin = datetime_to_unix(df["date"].min().date().replace(day=1))
    end = datetime_to_unix(df["date"].max().date() + datetime.timedelta(days=31))
    return begin, end


def get_category_options():
    return df["category"].unique()


def get_points_options():
    return sorted(df["points"].unique())[1:]


def get_date_range_object(prefix_component_id=""):
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
    return df["name"].unique()


def filter_song(song_name):
    return df[df["name"] == song_name]


def get_singers():
    return df["singer"].unique()


def filter_singer(singer_name):
    return df[df["singer"] == singer_name]


def filter_top_songs(songs_df, nb_songs):
    filter_top = (
        songs_df.groupby(by=["name"])["date"]
        .sum()
        .sort_values(ascending=False)
        .head(nb_songs)
    )
    songs_df = songs_df[songs_df["name"].isin(filter_top.index.to_list())]
    return songs_df


def compare_to_global(date_range, list_songs):
    table_totals = filter_date_totals(date_range)
    table_individual_songs = filter_date(date_range)
    table_individual_songs = table_individual_songs[
        table_individual_songs["name"].isin(list_songs)
    ]
    table_individual_songs = table_individual_songs.groupby(
        by=["name", "category", "points"], as_index=False
    )["date"].count()
    table_individual_songs = table_individual_songs.groupby(
        by=["category", "points"], as_index=False
    ).sum(numeric_only=True)
    table_totals = table_totals.merge(
        table_individual_songs,
        left_on=["category", "points"],
        right_on=["category", "points"],
    )
    table_totals["percent"] = table_totals["date"] / table_totals["total"]
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
