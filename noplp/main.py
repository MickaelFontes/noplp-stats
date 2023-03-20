"""Main module."""

from Scrapper import Scrapper

page = "Partir_un_jour"
scrap = Scrapper()
song_api = scrap.getSong(page=page)
print(song_api)
