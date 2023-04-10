"""Definition of the Song class."""

from dataclasses import dataclass
from datetime import date

@dataclass
class Song:
    """Class used to manage song instances imported from API data.
    Data recuperation is done byt the Scrapper class.
    Here, we simply define how data about each song is stored.

    Attributes:
        title: A string with the title of the song.
        lyrics: An string with the lyrics obtained from the Wiki API.
    """
    title: str
    singer: str
    lyrics: str
    dates: list[date]
    categories: list[str]
    points: list[int]
    emissions: list[int]


    def __str__(self) -> str:
        return f"Song instance of the title '{self.title}'"
