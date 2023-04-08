from functools import partial
from urllib import parse
import json
import multiprocessing
import requests


import pandas as pd

from Exceptions import (ScrapperTypePageError, ScrapperProcessingLyrics,
                        ScrapperProcessingDates, ScrapperProcessingPoints)
from Scrapper import Scrapper

def main():
    full_page_list = get_all_page_list(test=False)
    all_songs = []
    scrap = Scrapper(singer_required=False)
    pd.DataFrame({'title': full_page_list}).to_csv("data/songs.csv")
    individual_song_partial = partial(individual_song_scrap, scrap)
    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        all_songs = p.map(individual_song_partial, full_page_list)
    real_songs = []
    for song_maybe in all_songs:
        if song_maybe:
            real_songs.append(song_maybe)
    df = pd.DataFrame({'name': [song.title for song in real_songs for _ in range(len(song.dates))],
                 'singer': [song.singer for song in real_songs for _ in range(len(song.dates))],
                 'date': [date for song in real_songs for date in song.dates],
                 'category': [category for song in real_songs for category in song.categories],
                 'points': [point for song in real_songs for point in song.points]})
    df['date'] = pd.to_datetime(df['date'])
    df.to_csv('data/db_test_full.csv', index=False)

def individual_song_scrap(scrap, title):
    page_url = parse.quote(title, safe="")
    # print(title)
    try:
        song = scrap.getSong(page_url)
    except ScrapperTypePageError:
        print(f"'{title}' is NOT a relevant song page.")
        pass
    except ScrapperProcessingLyrics:
        print(f"'{title}' has no lyrics.")
    except ScrapperProcessingDates:
        print(f"'{title}' has no dates.")
    except ScrapperProcessingPoints:
        print(f"'{title}' has no POINTS.")
    except requests.exceptions.ConnectionError:
        #print()
        pass
    else:
        return song
        #print(f"'{title}' is a GOOD song page.")

def generate_url(start: int = 0, end: int = 500, limit: int = 500) -> str:
    return ("https://n-oubliez-pas-les-paroles.fandom.com/fr/api.php?"
           "action=query&"
           "format=json&"
           "prop=&list=backlinks&iwurl=1&ascii=1&bltitle=Liste_des_chansons_existantes&"
           f"blcontinue={start}%7C{end}&blnamespace=&bllimit={limit}")

def get_all_page_list(test: bool = True) -> list[str]:
    url: str
    if test:
        url = generate_url(0, 0, 500)
    else:
        url = generate_url(0, 0, 500)
    r: requests.Response = requests.get(url)
    data: dict = json.loads(r.text)
    pages_list: list[str] = [row['title'] for row in data['query']['backlinks']]
    while "continue" in data:
        if test:
            break
        start, end = data['continue']['blcontinue'].split('|', 1)
        print("while loop: ", start, end)
        url = generate_url(start=start, end=end)
        r = requests.get(url)
        data = json.loads(r.text)
        pages_list += [row['title'] for row in data['query']['backlinks']]


    print(len(pages_list))
    return pages_list

if __name__ == "__main__":
    main()
