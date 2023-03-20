"""Defnition of all exception types."""

class ScrapperError(Exception):
    """Generic Scrapper error."""

class ScrapperGetPageError(ScrapperError):
    """Error when reaching the API to get the song page."""

class ScrapperProcessingLyrics(ScrapperError):
    """Error when processing the source to extract the lyrics."""

class SongError(Exception):
    """Generic Song error."""
