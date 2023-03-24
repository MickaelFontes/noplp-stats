"""Definition of the Song class."""

from datetime import date
from typing import Union
class Song:
    """Class used to manage song instances imported from API data.
    Data recuperation is done byt the Scrapper class.
    Here, we simply define how data about each song is stored.

    Attributes:
        title: A string with the title of the song.
        lyrics: An string with the lyrics obtained from the Wiki API.
    """

    def __init__(self, title: str = '',
                 singer: str = '',
                 lyrics: str = '',
                 dates: Union[list[date], None] = None,
                 categories: Union[list[str], None] = None,
                 points: Union[list[int], None] = None):
        self.title = title
        self.singer = singer
        self.lyrics = lyrics
        if dates is None:
            self.dates = []
        else:
            self.dates = dates
        if categories is None:
            self.categories = []
        else:
            self.categories = categories
        if points is None:
            self.points = []
        else:
            self.points = points


    def __str__(self) -> str:
        return f"Song instance of the title '{self.title}'"
