from urllib import parse
import json
import requests


import pandas as pd

from Exceptions import ScrapperTypePageError, ScrapperProcessingLyrics, ScrapperProcessingDates
from Scrapper import Scrapper

def main():
    full_page_list = get_all_page_list(test=True)
    full_song_list = []
    scrap = Scrapper()
    nb_song = 0
    nb_lyrics = 0
    nb_dates = 0
    for title in full_page_list:
        try:
            page_url = parse.quote(title, safe="")
            song = scrap.getSong(page_url)
        except ScrapperTypePageError:
            #print(f"'{title}' is NOT a relevant song page.")
            pass
        except ScrapperProcessingLyrics:
            #print(f"'{title}' has no lyrics.")
            nb_lyrics += 1
        except ScrapperProcessingDates:
            #print(f"'{title}' has no dates.")
            nb_dates += 1
        except requests.exceptions.ConnectionError:
            #print()
            pass
        else:
            full_song_list.append(song)
            #print(f"'{title}' is a GOOD song page.")
            nb_song += 1
        print("==========")
        print("Full songs: ", nb_song)
        print("No dates: ", nb_dates)
        print("No lyrics: ", nb_lyrics)
    print("=====END=====")
    df = pd.DataFrame({'name': [song.title for song in full_song_list for _ in range(len(song.dates))],
                 'date': [date for song in full_song_list for date in song.dates]})
    df['date'] = pd.to_datetime(df['date'])
    df.to_csv('data/db_test.csv', index=False)

def generate_url(start: int = 0, end: int = 500, limit: int = 500) -> str:
    return ("https://n-oubliez-pas-les-paroles.fandom.com/fr/api.php?"
           "action=query&"
           "format=json&"
           "prop=&list=backlinks&iwurl=1&ascii=1&bltitle=Liste_des_chansons_existantes&"
           f"blcontinue={start}%7C{end}&blnamespace=&bllimit={limit}")

def get_all_page_list(test: bool = True) -> list[str]:
    url: str
    if test:
        url = generate_url(0, 25, 25)
    else:
        url = generate_url(0, 500)
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
