"""Script to create the songs database used for data visualization."""
from functools import partial
from urllib import parse
import json
import multiprocessing
import requests


import pandas as pd

from noplp.exceptions import (
    ScrapperTypePageError,
    ScrapperProcessingLyrics,
    ScrapperProcessingDates,
    ScrapperProcessingPoints,
    ScrapperProcessingEmissions,
)
from noplp.scrapper import Scrapper
from noplp.song import Song


def main():
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
    pd.DataFrame({"title": full_page_list}).to_csv("data/songs.csv")
    individual_song_partial = partial(individual_song_scrap, scrap)
    # Remove problematic and unrelevant songs
    if "Les feuilles mortes" in full_page_list:
        full_page_list.remove("Les feuilles mortes")
    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        all_songs = p.map(individual_song_partial, full_page_list)
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
    songs_df.to_csv("data/db_test_full.csv", index=False)


def individual_song_scrap(scrap: Scrapper, title: str) -> None | Song:
    """scrap a song page to create a Song

    Args:
        scrap (Scrapper): Scrapper object
        title (str): name of the song page URL

    Returns:
        None | song: Song object or nothing.
    """
    page_url = parse.quote(title, safe="")
    # print(title)
    try:
        song = scrap.get_song(page_url)
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
    else:
        # print(f"'{title}' is a GOOD song page.")
        return song
    return None


def generate_url(
    common_page: str, start: int = 0, end: int = 500, limit: int = 500
) -> str:
    """Generate URL to requests list of songs from the Fandom API.

    Args:
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


def get_all_page_list(common_songs_page: str, test: bool = True) -> list[str]:
    """Generate a list of all songs pages to download.

    Args:
        test (bool, optional): If the call is a short test. Defaults to True.

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


if __name__ == "__main__":
    main()
