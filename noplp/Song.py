"""Definition of the Song class."""

class Song:
    """Class used to manage song instances imported from API data.
    Data recuperation is done byt the Scrapper class.
    Here, we simply define how data about each song is stored.

    Attributes:
        title: A string with the title of the song.
        lyrics: An string with the lyrics obtained from the Wiki API.
    """

    def __init__(self, title: str = '', lyrics: str = ''):
        self.title: str = title
        self.lyrics: str = lyrics

    def __str__(self) -> str:
        return f"Song instance of the title {self.title}"
