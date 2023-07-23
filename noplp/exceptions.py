"""Defnition of all exception types."""


class ScrapperError(Exception):
    """Generic Scrapper error."""


class ScrapperTypePageError(ScrapperError):
    """The requested page is not a song page."""


class ScrapperGetPageError(ScrapperError):
    """Error when reaching the API to get the song page."""


class ScrapperProcessingSinger(ScrapperError):
    """Error when processing the source to extract the lyrics."""


class ScrapperProcessingLyrics(ScrapperError):
    """Error when processing the source to extract the lyrics."""


class ScrapperProcessingDates(ScrapperError):
    """Error when processing the source to extract the occurence dates."""


class ScrapperProcessingPoints(ScrapperError):
    """Error when processing the source to extract the points category."""


class ScrapperProcessingEmissions(ScrapperError):
    """Error when processing the source to extract the show number."""


class SongError(Exception):
    """Generic Song error."""
