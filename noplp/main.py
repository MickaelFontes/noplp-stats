"""Main module."""

import asyncio
import time

import aiohttp

from noplp.scrapper import Scrapper


async def main():
    """Small test for the Scrapper class."""
    start_time = time.time()
    scrap = Scrapper(singer_required=False)
    tasks = []
    songs = (
        "Stéréo",
        "Tandem",
        "Dis-moi",
        "Joe le taxi",
        "Ton invitation",
        "Lola",
        "Il avait les mots",
    )
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))

    for song in songs:
        task = asyncio.create_task(scrap.get_song(page=song, session=session))
        tasks.append(task)
    await asyncio.gather(*tasks)
    await session.close()

    time_difference = time.time() - start_time
    print(f"Scraping time: {time_difference:.2f} seconds.")
    # for i, cat in enumerate(song_api.categories):
    #     print(cat, ": ", song_api.emissions[i], song_api.dates[i], song_api.points[i])


if __name__ == "__main__":
    asyncio.run(main())
