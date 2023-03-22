"""Main module."""

from Scrapper import Scrapper

def main():
    page = "Mélissa"
    scrap = Scrapper()
    song_api = scrap.getSong(page=page)
    print(song_api.dates)

if __name__ == "__main__":
    main()
