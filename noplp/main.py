"""Main module."""

from noplp.scrapper import Scrapper


def main():
    """Small test for the Scrapper class.
    """
    page = "Ballade de Melody Nelson"
    scrap = Scrapper(singer_required=False)
    song_api = scrap.get_song(page=page)
    print(song_api.dates)


if __name__ == "__main__":
    main()
