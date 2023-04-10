"""Definition of the Scrapper class."""

from datetime import date
from typing import Tuple
import json
import re
import requests

import dateparser

from noplp.exceptions import (
    ScrapperGetPageError,
    ScrapperProcessingLyrics,
    ScrapperProcessingDates,
    ScrapperTypePageError,
    ScrapperProcessingPoints,
    ScrapperProcessingSinger,
    ScrapperProcessingEmissions,
)
from noplp.song import Song


class Scrapper:
    """Scrapper class used to obtain song from the Wiki.
    It creates Song instances parsing the API data.

    Attributes:
        data: A dictionnary of the data currently processed, obtained from the JSON API.
    """

    API_PAGE_ENDPOINT = (
        "https://n-oubliez-pas-les-paroles.fandom.com/fr/rest.php/v1/page/"
    )

    def __init__(self, singer_required: bool = False) -> None:
        self._title = ""
        self._data = {}
        self._singer_required = singer_required

    def check_relevant_song_page(self) -> bool:
        """Perform some check to see if the page is a song page we want.

        Returns:
            bool: True if relevant, else False
        """
        searched_words = [
            "[[Liste des chansons existantes|Retour à la liste des chansons]]",
            "Paroles",
            "Dates de sortie",
        ]

        if "Chanson non proposée" in self._data["source"]:
            return False

        return all(word in self._data["source"] for word in searched_words)

    def get_song(self, page: str) -> Song:
        """get the song page from the wiki API.
        Stores the response in the class instance.

        Args:
            page (str): JSON response of the API

        Raises:
            ScrapperGetPageError: Error when requesting the page.
            ScrapperGetPageError: The downloaded page is not a song page.

        Returns:
            song (Song): Song instance with the data obtained from the API
        """
        r = requests.get(Scrapper.API_PAGE_ENDPOINT + page, timeout=5)
        if r.status_code == 200:
            self._data = json.loads(r.text)
        else:
            raise ScrapperGetPageError(f"name: {r.url} ; {r.status_code}")

        # clean up source from problematic html tag
        self._data["source"] = (
            self._data["source"].replace("<u>", "").replace("</u>", "")
        )
        # Check this is a relevant song page
        if not self.check_relevant_song_page():
            raise ScrapperTypePageError(
                "The downloaded page source may not be a song page."
            )

        # Then extract and parse relevant data
        self._title = self._data["title"].replace('"', "")
        singer = self.extract_singer()
        lyrics = self.extract_lyrics()
        dates, categories, points, emissions = self.extract_dates()
        return Song(
            title=self._title,
            singer=singer,
            lyrics=lyrics,
            dates=dates,
            categories=categories,
            points=points,
            emissions=emissions,
        )

    def extract_singer(self) -> str:
        """Extracts the singer name from the source.

        Raises:
            ScrapperProcessingSinger: source is not available.
            ScrapperProcessingSinger: regex for singer failed.

        Returns:
            str: Name of the singer.
        """
        if self._data:
            source = self._data["source"]
        else:
            raise ScrapperProcessingSinger("data property empty.")

        # Extract singer from the source field
        regex_search = re.search(r"Interprète\w* : (.*)", source)
        if regex_search is not None:
            singer = regex_search.group(1)
            singer = singer.replace('"', "")
            return singer
        if self._singer_required:
            raise ScrapperProcessingSinger(
                "No singer found by the regex." + f"\n{self._title}"
            )
        return ""  # empty singer name if not required

    def extract_lyrics(self) -> str:
        """method used to extract the lyrcis from the source field obtained from the API.

        Raises:
            ScrapperProcessingLyrics: Error when applying the regex to extract lyrics.

        Returns:
            str: lyrics
        """
        if self._data:
            source = self._data["source"]
        else:
            raise ScrapperProcessingLyrics("data property empty." + f"\n{self._title}")

        # Extract lyrics from the source field
        regex_search = re.search(
            r"==\s{0,5}Paroles\s{0,5}(?:<.*>|)\s{0,5}==[^']*?(''[^=]*'')[\s\S]*?Dates de sortie",
            source,
        )
        if not regex_search:
            raise ScrapperProcessingLyrics(
                "No lyrics found by the regex." + f"\n{self._title}"
            )
        lyrics = regex_search.group(1)
        lyrics = lyrics.replace("'\n\n'", "'\n'").replace("\n\n", "\n")
        lyrics = lyrics.replace("'''", "").replace("''", "").replace("’", "'")
        return lyrics

    def extract_dates(self) -> Tuple[list[date], list[str], list[int], list[int]]:
        """Method to extract the occurence dates of the song from the page source.

        Extract the relevant section from source, then matches each relevant line and calls
        process_date_line() to parse it.

        Raises:
            ScrapperProcessingLyrics: Page source not found.
            ScrapperProcessingDates: Relevant dates section not found.
            ScrapperProcessingDates: No date lines found.

        Returns:
            list[date]: List of all occurence dates of the song.
        """
        # First, select only the target section
        dates: list[date] = []
        categories: list[str] = []
        points: list[int] = []
        emissions: list[int] = []
        if self._data:
            source: str = self._data["source"]
        else:
            raise ScrapperProcessingDates("data property empty." + f"\n{self._title}")
        regex_section = re.search(
            r"==\s{0,5}Dates de sortie\s{0,5}==[\S\s]*?==\s{0,5}Trous\s{0,5}==", source
        )
        if regex_section:
            section = regex_section.group(0)
        else:
            raise ScrapperProcessingDates(
                "No dates section found by the regex." + f"\n{self._title}"
            )
        # Then extract each line with an occurence date
        regex_each_date = re.findall(r"#.*", section)
        if regex_each_date:
            for song_date_line in regex_each_date:
                if re.match(r"^#\S*$", song_date_line):  # empty line
                    continue
                song_date_line = song_date_line.replace("'", "")
                dates.append(self.process_date_line(song_date_line))
                category, point = self.process_points_line(song_date_line)
                if category == "Points":  # for "émission"
                    emission = self.process_emission_line(song_date_line)
                else:
                    emission = 0
                categories.append(category)
                points.append(point)
                emissions.append(emission)
        else:
            raise ScrapperProcessingDates(
                "No date lines found by the regex." + f"\n{self._title}"
            )
        return dates, categories, points, emissions

    def process_date_line(self, line: str) -> date:
        """Process a string line date to return the occurence date.

        Args:
            line (str): Line of the page source

        Raises:
            ScrapperProcessingDates: No known date pattern found in the line.
            ScrapperProcessingDates: Did not manage to process the date.

        Returns:
            date: Date of song occurence.
        """
        regex_date = re.search(r"\w+\s+\d+\w*\s+\w+\s+\d+", line)
        if not regex_date:
            raise ScrapperProcessingDates(
                "No date found in the provided line\n\n" + line + f"\n{self._title}"
            )
        date_text = regex_date.group()
        # # Then remove eventual letter in date number (eg: 1er, 2e, etc.)
        # date = re.sub(r"(\d+)[a-zA-Z]+",r"\1", date)
        # -> No need, dateparser does the job
        date_object = dateparser.parse(date_text)
        if not date_object:
            raise ScrapperProcessingDates(
                "Did not manage to parse the date.\n\n" + date_text + f"\n{self._title}"
            )
        return date_object.date()  # We only care about the date

    def process_points_line(self, line: str) -> Tuple[str, int]:
        """Processes a date line to extract points category.

        Args:
            line (str): line of a date occurence.

        Raises:
            ScrapperProcessingPoints: No category have been extracted.

        Returns:
            Tuple[str, int]: category name, nb of points if any.
        """
        regex = re.search(
            r"(\d\w\s{0,5}?(point|prise)|Même chanson|Maestro|Chanson piégée|Chanson à trou|Tournoi)",
            line,
        )
        if regex:
            points_text = regex.group(1)
            checks = ["point", "prise"]
            if not any(x in points_text for x in checks):
                return points_text, -1
            return "Points", int(points_text[0] + "0")  # manual fix for found typos
        # No most exepected category found
        regex_extract = re.search(r"\s*((\w+\s)*\w+)\s*:", line)
        if not regex_extract:
            raise ScrapperProcessingPoints(
                "No points category found in the line\n\n" + line + f"\n{self._title}"
            )
        return regex_extract.group(1), -1

    def process_emission_line(self, line: str) -> int:
        """Return the show/emission number.
        Strictly positive if usual emission.

        Args:
            line (str): line of date occurrence

        Raises:
            ScrapperProcessingEmissions: line contains "émission"
            or "rencontre" but no number found.

        Returns:
            int: occurence number
        """
        regex_numero = re.search(
            r"(?:;|:|-|,|)\s{,3}(\d)\w{,4}\s{,4}\w{,7}(?:sion|ontre)", line
        )
        factor = 1
        # if not usual emission
        if any(
            [
                word in line.lower()
                for word in [
                    "tournoi",
                    "ligue",
                    "spécial",
                    "prime",
                    "ontre",
                    "master",
                    "enfants",
                ]
            ]
        ):
            factor = -1

        if regex_numero:
            emission = int(regex_numero.group(1))
            return emission * factor
        elif "unique" in line:
            return 0
        else:
            if "sion" in line or "ontre" in line:
                raise ScrapperProcessingEmissions(
                    "No show number found in the line\n\n" + line + f"\n{self._title}"
                )
            else:
                return 0
