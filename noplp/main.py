"""Main module."""

from noplp.scrapper import Scrapper


def main():
    """Small test for the Scrapper class."""
    page = "Avenir"
    scrap = Scrapper(singer_required=False)
    song_api = scrap.get_song(page=page)

    print(song_api.title)
    print(song_api.singer)
    # for i, cat in enumerate(song_api.categories):
    #     print(cat, ": ", song_api.emissions[i], song_api.dates[i], song_api.points[i])


if __name__ == "__main__":
    main()
