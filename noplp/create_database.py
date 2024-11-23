"""Script to create the song database used for data visualization."""

import argparse
import asyncio
import json
import time
from random import sample
from urllib import parse

import aiohttp
import pandas as pd
import requests
from requests.exceptions import ReadTimeout

from noplp.exceptions import (
    ScrapperProcessingDates,
    ScrapperProcessingEmissions,
    ScrapperProcessingLyrics,
    ScrapperProcessingPoints,
    ScrapperTypePageError,
)
from noplp.scrapper import Scrapper
from pages.utils import filter_date, get_time_limits


async def global_scrapping(test: bool) -> pd.DataFrame:
    """Performs the whole Scrapper logic to download all songs information
    from the Fandom Wiki.
    """
    full_page_list: list[str] = []
    common_song_pages = [
        "Liste_des_chansons_existantes",
        "Liste_des_chansons_existantes_(de_la_lettre_A_à_la_lettre_M)",
        "Liste_des_chansons_existantes_(de_la_lettre_N_à_la_lettre_Z)",
    ]
    for common_song_page in common_song_pages:
        full_page_list += get_all_page_list(common_song_page, test=False)
    full_page_list = list(set(full_page_list))
    all_songs = []
    scrap = Scrapper(singer_required=False)
    pd.DataFrame({"title": full_page_list}).sort_values(by="title").to_csv(
        "data/songs.csv", index=False
    )
    # Remove problematic and unrelevant songs
    if "Les feuilles mortes" in full_page_list:
        full_page_list.remove("Les feuilles mortes")

    # Scrapping all.
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
    tasks = []
    if test:
        full_page_list = sample(full_page_list, 150)
        full_page_list += ["2 be 3", "Je sais pas"]
        full_page_list = list(set(full_page_list))

    for page in full_page_list:
        task = asyncio.create_task(
            individual_song_scrap(scrap, page, session, all_songs)
        )
        tasks.append(task)
    await asyncio.gather(*tasks)
    await session.close()

    # Saving scrapped data.
    real_songs = []
    for song_maybe in all_songs:
        if song_maybe:
            real_songs.append(song_maybe)
    songs_df = pd.DataFrame(
        {
            "name": [song.title for song in real_songs for _ in range(len(song.dates))],
            "singer": [
                song.singer for song in real_songs for _ in range(len(song.dates))
            ],
            "date": [date for song in real_songs for date in song.dates],
            "category": [
                category for song in real_songs for category in song.categories
            ],
            "points": [point for song in real_songs for point in song.points],
            "emissions": [
                emission for song in real_songs for emission in song.emissions
            ],
        }
    )
    songs_df["date"] = pd.to_datetime(songs_df["date"])
    songs_df.sort_values(ascending=True, by=["name", "singer", "date"], inplace=True)
    songs_df.to_csv("data/db_test_full.csv", index=False)
    lyrics_df = pd.DataFrame(
        {
            "name": [song.title for song in real_songs],
            "singer": [song.singer for song in real_songs],
            "lyrics": [song.lyrics.replace("\n", "\\n") for song in real_songs],
        }
    )
    lyrics_df.sort_values(ascending=True, by=["name", "singer"], inplace=True)
    lyrics_df.to_csv("data/db_lyrics.csv", index=False)


async def individual_song_scrap(
    scrap: Scrapper, title: str, session: aiohttp.ClientSession, all_songs: pd.DataFrame
) -> None:
    """scrap a song page to create a Song

    Args:
        scrap (Scrapper): Scrapper object
        title (str): name of the song page URL
        session (aiohttp.ClientSession): HTTP client session
        all_songs (pd.Dataframe): Dataframe where song is added

    Returns:
        None: nothing.
    """
    page_url = parse.quote(title, safe="")
    try:
        song = await scrap.get_song(page_url, session)
    except ScrapperTypePageError:
        print(f"'{title}' is NOT a relevant song page.")
    except ScrapperProcessingLyrics:
        print(f"'{title}' has no lyrics.")
        # pass
    except ScrapperProcessingDates:
        print(f"'{title}' has no dates.")
        # pass
    except ScrapperProcessingPoints:
        print(f"'{title}' has no POINTS.")
        # pass
    except requests.exceptions.ConnectionError:
        # print()
        pass
    except ScrapperProcessingEmissions:
        print(f"'{title}' has no SHOW NUMBER.")
    except ReadTimeout:
        time.sleep(30)
        return individual_song_scrap(scrap, title, session, all_songs)
    else:
        # print(f"'{title}' is a GOOD song page.")
        all_songs.append(song)
    return None


def generate_url(
    common_page: str, start: int = 0, end: int = 500, limit: int = 500
) -> str:
    """Generate URL to request list of songs from the Fandom API.

    Args:
        common_page (str): page used to look for backlinks.
        start (int, optional): index start. Defaults to 0.
        end (int, optional): index end. Defaults to 500.
        limit (int, optional): maximum number of songs returned by the request. From 1 to 500. Defaults to 500.

    Returns:
        str: URL for request with all parameters.
    """
    return (
        "https://n-oubliez-pas-les-paroles.fandom.com/fr/api.php?"
        "action=query&"
        "format=json&"
        f"prop=&list=backlinks&iwurl=1&ascii=1&bltitle={common_page}&"
        f"blcontinue={start}%7C{end}&blnamespace=&bllimit={limit}"
    )


def get_all_page_list(common_songs_page: str, test: bool = False) -> list[str]:
    """Generate a list of all songs pages to download.

    Args:
        common_songs_page (str): page used to look for backlinks.
        test (bool, optional): If the call is a short test. Defaults to False.

    Returns:
        list[str]: List of all songs title to request.
    """
    url: str
    if test:
        url = generate_url(common_songs_page, 0, 0, 500)
    else:
        url = generate_url(common_songs_page, 0, 0, 500)
    r: requests.Response = requests.get(url, timeout=5)
    data: dict = json.loads(r.text)
    pages_list: list[str] = [row["title"] for row in data["query"]["backlinks"]]
    while "continue" in data:
        if test:  # we do not query the whole songs list
            break
        start, end = data["continue"]["blcontinue"].split("|", 1)
        print("while loop: ", start, end)
        url = generate_url(common_songs_page, start=start, end=end)
        r = requests.get(url, timeout=5)
        data = json.loads(r.text)
        pages_list += [row["title"] for row in data["query"]["backlinks"]]

    print(len(pages_list))
    return pages_list


def return_df_cumsum_category(songs_df: pd.DataFrame, category: str) -> pd.DataFrame:
    """Compute cumulative sum for songs coverage.

    Args:
        songs_df (Dataframe): songs dataframe of selected timeframe
        category (str): Song category

    Returns:
        Dataframe: Dataframe with "nb" column as cumulative sum
    """
    if category == "TOUT":
        same_base_df = songs_df
        same_base_df["category"] = "TOUT"
    else:
        same_base_df = songs_df[songs_df["category"] == category]
    # 1: Order songs by descending (after groupby(date, emissions))
    songs_ranking = (
        same_base_df.groupby(by=["name"], as_index=False)[["date"]]
        .count()
        .sort_values(by=["date"], ascending=False)
    )
    songs_ranking.drop_duplicates(inplace=True)
    # 2: Calculate denopminator (date, emissions)
    denominator_df = same_base_df.groupby(by=["date", "emissions"], as_index=False)[
        "singer"
    ].count()
    denominator_df.drop_duplicates(inplace=True)
    denominator = len(denominator_df)
    # 3: For each song, merge first selected songs (remove duplicates)
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
    songs_ranking["category"] = (
        category.split(" ", 1)[1] if "-1" in category else category
    )
    songs_ranking["coverage"] = iter_coverage
    return songs_ranking


def compute_cumulative_graph() -> None:
    """Computes and saves the global coverage graph data."""
    # 1. Read new CSV version
    df_new = pd.read_csv("data/db_test_full.csv", index_col=None)
    df_new["date"] = pd.to_datetime(df_new["date"])
    df_new["singer"] = df_new["singer"].astype("str")
    df_new["name"] = df_new["name"].astype("str")

    # Filters and compute graphs
    date_range = get_time_limits(data_frame=df_new)
    graph_df = filter_date(date_range, data_frame=df_new)
    graph_df["category"] = graph_df["points"].astype(str) + " " + graph_df["category"]
    graph_maestro = return_df_cumsum_category(graph_df, "-1 Maestro")
    graph_50 = return_df_cumsum_category(graph_df, "50 Points")
    graph_40 = return_df_cumsum_category(graph_df, "40 Points")
    graph_30 = return_df_cumsum_category(graph_df, "30 Points")
    graph_meme = return_df_cumsum_category(graph_df, "-1 Même chanson")

    # 3. Export results
    return_df_cumsum_category(graph_df, "TOUT").sort_values(
        by=["name", "category"]
    ).to_csv("data/global_ranking.csv", index=False)
    graph_all = pd.concat([graph_maestro, graph_50, graph_40, graph_30, graph_meme])
    graph_all.sort_values(by=["category", "rank"], inplace=True)
    graph_all.to_csv("data/coverage_graph.csv", index=False)


async def main(test: bool):
    """Run the whole scrapping and computations logic."""
    await global_scrapping(test=test)
    compute_cumulative_graph()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Perform scrapping for NOPLP database."
    )
    parser.add_argument(
        "--test", "-t", action=argparse.BooleanOptionalAction, default=False
    )
    args = parser.parse_args()
    asyncio.run(main(test=args.test))
