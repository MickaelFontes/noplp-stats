"""Main module."""

from Scrapper import Scrapper

def main():
    page = "Ballade de Melody Nelson"
    scrap = Scrapper(singer_required=False)
    song_api = scrap.getSong(page=page)
    print(song_api.dates)

if __name__ == "__main__":
    main()
