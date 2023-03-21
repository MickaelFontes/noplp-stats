"""Definition of the Scrapper class."""

from datetime import date
import json
import re
import requests

import dateparser

from Exceptions import ScrapperGetPageError, ScrapperProcessingLyrics, ScrapperProcessingDates
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
        dates = self.extractDates()
        return Song(title=title, lyrics=lyrics, dates=dates)

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

    def extractDates(self) -> list[date]:
        """Method to extract the occurence dates of the song from the page source.
        
        Extract the relevant section from source, then matches each relevant line and calls
        processDateLine() to parse it.

        Raises:
            ScrapperProcessingLyrics: Page source not found.
            ScrapperProcessingDates: Relevant dates section not found.
            ScrapperProcessingDates: No date lines found.

        Returns:
            list[date]: List of all occurence dates of the song.
        """
        # First, select only the target section
        dates: list[date] = []
        if self.data:
            source: str = self.data['source']
        else:
            raise ScrapperProcessingDates('data property empty.')
        regex_section = re.search(r"== Dates de sortie ==[\S\s]*?== Trous ==", source)
        if regex_section:
            section = regex_section.group(0)
        else:
            raise ScrapperProcessingDates('No dates section found by the regex.')
        # Then extract each line with an occurence date
        regex_each_date = re.findall(r"#.*", section)
        if regex_each_date:
            for song_date in regex_each_date:
                dates.append(self.processDateLine(song_date))
        else:
            raise ScrapperProcessingDates('No date lines found by the regex.')
        return dates

    @staticmethod
    def processDateLine(line: str) -> date:
        """Process a string line date to return the occurence date.

        Args:
            line (str): Line of the page source

        Raises:
            ScrapperProcessingDates: No known date pattern found in the line.
            ScrapperProcessingDates: Did not manage to process the date.

        Returns:
            date: Date of song occurence.
        """
        regex_date = re.search(r"\|(\w* \w* \w* \w*)( ;|])", line)
        if regex_date:
            date_text = regex_date.group(1)
            # # Then remove eventual letter in date number (eg: 1er, 2e, etc.)
            # date = re.sub(r"(\d+)[a-zA-Z]+",r"\1", date)
            # -> No need, dateparser does the job
            date_object = dateparser.parse(date_text)
            if date_object:
                return date_object.date() # We only care about the date
            else:
                raise ScrapperProcessingDates('Did not manage to parse the date.\n\n' + date_text)
        else:
            raise ScrapperProcessingDates('No date found in the provided line\n\n' + line)
        