"""Training page to guess songs lyrics."""
import re

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, html
from unidecode import unidecode

from pages.utils import get_song_dropdown_menu, return_lyrics_df

dash.register_page(__name__, path="/training")

layout = html.Div(
    [
        html.H5("Zone d'entraînement pour apprendre les paroles"),
        html.P(
            "Choisissez uen chanson et tapez ses paroles pour vérifier si vous les connaissez !"
        ),
        get_song_dropdown_menu(),
        html.Hr(),
        dbc.Textarea(
            id="user-lyrics",
            className="mb-3",
            placeholder="Tapez les paroles de la chanson...",
        ),
        dbc.Button("Vérifier les paroles", id="btn-check-lyrics"),
        html.Div(id="verified-lyrics"),
    ]
)


@callback(
    Output("verified-lyrics", "children"),
    Input("user-lyrics", "value"),
    Input("dropdown-song", "value"),
)
def compare_text_and_lyrics(user_text, song_title):
    """Compare user input text and known lyrics, return a comment on error or match.

    Args:
        user_text (str): user input lyrics
        song_title (str): song title

    Returns:
        list[hmtl]|str: List of Dash html components
    """
    if user_text:
        lyrics_df = return_lyrics_df()
        lyrics = lyrics_df[lyrics_df["name"] == song_title]["lyrics"].values[0]

        user_words = [x for x in re.split(r" |'", user_text.replace("\n", " ")) if x != ""]
        lyrics_words = [x for x in re.split(r" |'", lyrics.replace("\\n", " ")) if x != ""]

        for i, word in enumerate(user_words):
            if unidecode(word.lower()) == unidecode(lyrics_words[i].lower()):
                continue
            else:
                return [html.P("Mistake after: " + " ".join(user_words[: i + 1][-5:])), html.Br(),
                        html.P("Expected words: " + " ".join(lyrics_words[: i + 1][-5:]))]
        return "All user words are valid"
    return ""
