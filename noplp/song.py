"""Definition of the Song class."""

from dataclasses import dataclass
from datetime import date
<<<<<<< HEAD:noplp/song.py
from typing import Union


=======

@dataclass
>>>>>>> c5dcb20 (♻️ Switch Song for dataclass and add show number):noplp/Song.py
class Song:
    # pylint: disable=too-few-public-methods
    """Class used to manage song instances imported from API data.
    Data recuperation is done byt the Scrapper class.
    Here, we simply define how data about each song is stored.

    Attributes:
        title: A string with the title of the song.
        lyrics: An string with the lyrics obtained from the Wiki API.
    """
<<<<<<< HEAD:noplp/song.py

    def __init__(
        self,
        title: str = "",
        singer: str = "",
        lyrics: str = "",
        dates: Union[list[date], None] = None,
        categories: Union[list[str], None] = None,
        points: Union[list[int], None] = None,
    ):
        # pylint: disable=too-many-arguments
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
=======
    title: str
    singer: str
    lyrics: str
    dates: list[date]
    categories: list[str]
    points: list[int]
    emissions: list[int]
>>>>>>> c5dcb20 (♻️ Switch Song for dataclass and add show number):noplp/Song.py

    def __str__(self) -> str:
        return f"Song instance of the title '{self.title}'"
