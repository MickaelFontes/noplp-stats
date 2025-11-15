"""Definition of the Scrapper class."""

import json
import re
from datetime import date

import aiohttp
import dateparser
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup

from noplp.exceptions import (
    ScrapperGetPageError,
    ScrapperProcessingDates,
    ScrapperProcessingEmissions,
    ScrapperProcessingLyrics,
    ScrapperProcessingPoints,
    ScrapperProcessingSinger,
    ScrapperTypePageError,
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

    def __init__(
        self,
        singer_required: bool = False,
        ratelimit: AsyncLimiter = AsyncLimiter(1, 0.01),
    ) -> None:
        self._title = ""
        self._data = {}
        self._singer_required = singer_required
        self._ratelimit = ratelimit

    def check_relevant_song_page(self) -> bool:
        """Perform some check to see if the page is a song page we want.

        Returns:
            bool: True if relevant, else False
        """
        searched_words = [
            "[[Liste des chansons existantes",
            "|Retour à la liste des chansons]]",
            "Paroles",
            "Dates de sortie",
        ]

        if "Chanson non proposée" in self._data["source"]:
            return False

        return all(word in self._data["source"] for word in searched_words)

    async def get_song(self, page: str, session: aiohttp.ClientSession) -> Song:
        """get the song page from the wiki API.
        Stores the response in the class instance.

        Args:
            page (str): JSON response of the API
            session (aiohttp.ClientSession): HTTP client session

        Raises:
            ScrapperGetPageError: Error when requesting the page.
            ScrapperGetPageError: The downloaded page is not a song page.
            ScrapperTypePageError: The page does not appear to be a song page.

        Returns:
            song (Song): Song instance with the data obtained from the API
        """
        async with self._ratelimit:
            async with session.get(Scrapper.API_PAGE_ENDPOINT + page) as response:
                if (status_code := response.status) == 200:
                    text = await response.text()
                    self._data = json.loads(text)
                else:
                    raise ScrapperGetPageError(f"name: {response.url} ; {status_code}")

        # clean up source from problematic html tag
        soup = BeautifulSoup(self._data["source"], "html.parser")
        u_tags = soup.find_all("u")
        for u in u_tags:
            u.unwrap()
        ref_tags = soup.find_all("ref")
        for ref in ref_tags:
            ref.decompose()
        br_tags = soup.find_all("br")
        for br in br_tags:
            br.decompose()
        self._data["source"] = soup.get_text()

        # Check this is a relevant song page
        if not self.check_relevant_song_page():
            raise ScrapperTypePageError(
                "The downloaded page source may not be a song page."
            )

        # Then extract and parse relevant data
        self._title = self._data["title"].replace('"', "").strip()
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
        if (
            regex_search := re.search(r"(?:Auteur|Interprète)\w* : (.*)", source)
        ) is not None:
            singer = regex_search.group(1)
            # discard potential following brackets
            singer = re.search(r"([^\[]*)", singer).group(1)
            singer = singer.replace('"', "")
            return singer.strip()
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
            r"==[\s']{0,5}Paroles[\s']{0,5}(?:<.*>|)\s{0,5}==[^']*?(''[^=]*'')[\s\S]*?Dates de sortie",
            source,
        )
        if not regex_search:
            raise ScrapperProcessingLyrics(
                "No lyrics found by the regex." + f"\n{self._title}"
            )

        def multiple_inline_parenthesis(text):
            """Replace inline repetition parenthesis by the repeated lyrics."""

            def replace_line(matchobj):
                i = int(matchobj.group(2))
                string_multiplied = (matchobj.group(1) + matchobj.group(3)) + (
                    i - 1
                ) * ("\n" + matchobj.group(1) + matchobj.group(3))
                return string_multiplied

            find_multiply = re.sub(
                r"^(.{3,})\(\s{,2}[x*X]\s{,2}([0-9]+)\s{,2}\)(.*)$",
                replace_line,
                text,
                flags=re.MULTILINE,
            )
            return find_multiply

        def multiply_paragraph_prefix(text):
            """Replace paragaph repetition parenthesis by the repeated lyrics."""

            def replace_paragraph(matchobj):
                i = int(matchobj.group(1))
                string_multiplied = (
                    matchobj.group(2) + (i - 1) * ("\n" + matchobj.group(2)) + "\n\n"
                )
                return string_multiplied

            find_multiply_p = re.sub(
                r"^[' ]{,5}\(.{,2}[x*X].{,2}([0-9]+).{,2}\)[' ]{,4}$\n([\s\S]*?)(?:\n\n)",
                replace_paragraph,
                text,
                flags=re.MULTILINE,
            )
            return find_multiply_p

        def process_raw_lyrics(lyrics):
            """Expand repititions patterns in lyrics."""
            lyrics = multiply_paragraph_prefix(lyrics)
            lyrics = multiple_inline_parenthesis(lyrics)
            return lyrics

        lyrics = regex_search.group(1) + "\n\n\n"
        lyrics = lyrics.replace("'\n\n'", "'\n'").replace("\n\n", "\n")
        lyrics = process_raw_lyrics(lyrics)
        lyrics = re.sub(r"'''(.*)'''", r"¤\1", lyrics)
        lyrics = lyrics.replace("''", "").replace("’", "'").replace(" ", "")
        lyrics = lyrics.replace("' '", " ")
        return lyrics.strip()

    def extract_dates(self) -> tuple[list[date], list[str], list[int], list[int]]:
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
            r"==[\s']{0,5}Dates de sortie[\s']{0,5}==[\S\s]*?==[\s']{0,5}Trous[\s']{0,5}==",
            source,
        )
        if regex_section:
            section = regex_section.group(0)
        else:
            raise ScrapperProcessingDates(
                "No dates section found by the regex." + f"\n{self._title}"
            )
        # Then extract each line with an occurence date
        if regex_each_date := re.findall(r"#.*", section):
            for song_date_line in regex_each_date:
                if re.match(r"^#\S*$", song_date_line):  # empty line
                    continue
                song_date_line = song_date_line.replace("'", "")
                dates.append(self.process_date_line(song_date_line))
                category, point = self.process_points_line(song_date_line)
                emission = self.process_emission_line(song_date_line)
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
        if not (regex_date := re.search(r"\w+\s+\d+\w*\s+\w+\s+\d+", line)):
            raise ScrapperProcessingDates(
                "No date found in the provided line\n\n" + line + f"\n{self._title}"
            )
        date_text = regex_date.group()
        # # Then remove eventual letter in date number (eg: 1er, 2e, etc.)
        # date = re.sub(r"(\d+)[a-zA-Z]+",r"\1", date)
        # -> No need, dateparser does the job
        if not (date_object := dateparser.parse(date_text)):
            raise ScrapperProcessingDates(
                "Did not manage to parse the date.\n\n" + date_text + f"\n{self._title}"
            )
        return date_object.date()  # We only care about the date

    def process_points_line(self, line: str) -> tuple[str, int]:
        """Processes a date line to extract points category.

        Args:
            line (str): line of a date occurence.

        Raises:
            ScrapperProcessingPoints: No category have been extracted.

        Returns:
            Tuple[str, int]: category name, nb of points if any.
        """
        regex = re.search(
            r"(\d\w\s{0,5}?(point|prise)|Même chanson|Maestro|Chanson piégée|Chanson à trou|Tournoi|Tirée|mots imposés)",
            line,
            flags=re.IGNORECASE,
        )
        if regex:
            points_text = regex.group(1)
            checks = ["point", "prise"]
            if not any(x in points_text.lower() for x in checks):
                return points_text.capitalize(), -1
            return "Points", int(points_text[0] + "0")  # manual fix for found typos
        if regex_money := re.search(r"(\d*\s{0,2}\d+)\s{0,5}€", line):
            gain = regex_money.group(1)
            gain = re.sub(r"[^\d]", "", gain)
            gain = int(gain)
            return "Ancienne formule", gain
        # No most exepected category found
        if not (regex_extract := re.search(r"\s*((\w+\s)*\w+)\s*:", line)):
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
            r"(?:;|:|-|,|)\s{,3}(\d)\w{,4}\s{,4}\w{,7}(?:sion|ontre|duo|émi)", line
        )
        factor = 1
        # if not usual emission
        if any(
            word in line.lower()
            for word in (
                "tournoi",
                "ligue",
                "spécial",
                "prime",
                "ontre",
                "master",
                "enfants",
            )
        ):
            factor = -1

        if regex_numero:
            emission = int(regex_numero.group(1))
            return emission * factor
        if "unique" in line:
            return 0
        if ("mi" in line and "sion" in line) or "ontre" in line:
            raise ScrapperProcessingEmissions(
                "No show number found in the line\n\n" + line + f"\n{self._title}"
            )
        # else, default number
        return 0
