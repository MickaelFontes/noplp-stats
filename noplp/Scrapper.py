"""Definition of the Scrapper class."""

import json
import re
import requests

from Exceptions import ScrapperGetPageError, ScrapperProcessingLyrics
from Song import Song

class Scrapper:
    """Scrapper class used to obtain song from the Wiki.
    It creates Song instances parsing the API data.
    
    Attributes:
        data: A dictionnary of the data currently processed, obtained from the JSON API.
    """

    API_PAGE_ENDPOINT = "https://n-oubliez-pas-les-paroles.fandom.com/fr/rest.php/v1/page/"

    def __init__(self) -> None:
        self.data = None

    def getSong(self, page :str) -> Song:
        """get the song page from the wiki API.
        Stores the response in the class instance.

        Args:
            page (str): JSON response of the API

        Raises:
            ScrapperError: if no page is found
            
        Returns:
            song (Song): Song instance with the data obtained from the API
        """
        r = requests.get(Scrapper.API_PAGE_ENDPOINT + page)
        if r.status_code == 200:
            print("API response: HTTP 200")
            self.data = json.loads(r.text)
        else:
            raise ScrapperGetPageError(r.status_code)
        title = self.data['title']
        lyrics = self.extractLyrics()
        return Song(title=title, lyrics=lyrics)

    def extractLyrics(self) -> str:
        """method used to extract the lyrcis from the source field obtained from the API.

        Raises:
            ScrapperProcessingLyrics: Error when applying the regex to extract

        Returns:
            str: lyrics
        """
        if self.data:
            source = self.data['source']
        else:
            raise ScrapperProcessingLyrics('data property empty.')

        #Extract lyrics from the source field
        regex_search = re.search(r"== Paroles ==[\s\S]*?(''[\s\S]*'')[\s\S]*?== Dates de sortie ==",
                                 source)
        if regex_search is not None:
            lyrics = regex_search.group(1)
            lyrics = lyrics.replace("'\n\n'", "'\n'").replace("\n\n", "\n")
            lyrics = lyrics.replace("'''", "").replace("''", "").replace("’", "'")
            return lyrics
        else:
            raise ScrapperProcessingLyrics('No lyrics found by the regex.')
