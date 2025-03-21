"""Training page to guess songs lyrics."""

import re

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html
from unidecode import unidecode

from pages.utils import (
    extract_and_format_lyrics,
    get_song_dropdown_menu,
    return_lyrics_df,
)

dash.register_page(__name__, path="/training", title="Entraînement - NOLPL stats")

layout = dbc.Container(
    [
        html.H5("Zone d'entraînement pour apprendre les paroles"),
        html.P(
            "Choisissez une chanson et tapez ses paroles pour vérifier si vous les connaissez !"
        ),
        get_song_dropdown_menu(),
        html.Hr(),
        dbc.Textarea(
            id="user-lyrics",
            className="mb-3",
            placeholder="Tapez les paroles de la chanson...",
            style={"height": 200},
        ),
        html.Div(id="verified-lyrics"),
        dbc.Progress(id="user-lyrics-progress", value=0),
        html.Hr(),
        dbc.Button(
            "Montrer les paroles vérifiées",
            id="collapse-button",
            className="mb-3",
            color="primary",
            n_clicks=0,
        ),
        dbc.Collapse(
            dbc.Card(id="collasped-verified-lyrics", body=True),
            id="collapse",
            is_open=False,
        ),
    ],
    style={"marginTop": 20},
)


@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(nb_clicks: int, is_open: bool):
    """Collapse or expand when button is clicked.

    Args:
        nb_clicks (int): number of clicks
        is_open (bool): State boolean for collapse State

    Returns:
        bool: New state boolean for collapse State
    """
    if nb_clicks:
        return not is_open
    return is_open


@callback(
    Output("verified-lyrics", "children"),
    Output("collasped-verified-lyrics", "children"),
    Output("user-lyrics-progress", "value"),
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
        puntuaction_marks = [",", ";", ":", "?", "!", "."]
        user_text = remove_multiple_strings(user_text, puntuaction_marks)
        lyrics_df = return_lyrics_df()
        raw_lyrics = lyrics_df[lyrics_df["name"] == song_title]["lyrics"].values[0]
        lyrics = raw_lyrics.replace("¤", "")

        # Remove optional text inside parenthesis or brackets and punctuation marks
        lyrics = re.sub(r"\([^()]*?\)", r"", lyrics, flags=re.MULTILINE)
        lyrics = re.sub(r"\[[^\[\])]*?\]", r"", lyrics, flags=re.MULTILINE)
        lyrics = remove_multiple_strings(lyrics, puntuaction_marks)

        user_words = [
            x for x in re.split(r" |'|-", user_text.replace("\n", " ")) if x != ""
        ]
        lyrics_words = [
            x for x in re.split(r" |'|-", lyrics.replace("\\n", " ")) if x != ""
        ]
        verified_lyrics = []
        user_progress = 0
        for i, word in enumerate(user_words):
            if unidecode(word.lower()) != unidecode(lyrics_words[i].lower()):
                verified_lyrics, user_progress = get_lyrics_approx_until_cut(
                    raw_lyrics, len(lyrics_words), i + 1
                )
                return (
                    [
                        html.P(
                            "⛔ Erreur, paroles tapées incorrectes: "
                            + " ".join(user_words[: i + 1][-5:])
                        ),
                        html.Br(),
                        html.P(
                            "Paroles attendues: " + " ".join(lyrics_words[: i + 1][-5:])
                        ),
                    ],
                    verified_lyrics,
                    user_progress,
                )
        verified_lyrics, user_progress = get_lyrics_approx_until_cut(
            raw_lyrics, len(lyrics_words), len(user_words) + 1
        )
        return "✅ Tous les mots tapés sont valides !", verified_lyrics, user_progress
    return "", "", 0


def get_lyrics_approx_until_cut(lyrics: str, nb_total_words: int, nb_found_words: int):
    """Returns lyrics to approximately display only what the user type, with the verified version.

    Args:
        lyrics (str): raw str from lyrics db
        nb_total_words (int): Total number of words to guess
        nb_found_words (int): Number of words found by the user

    Returns:
        str, int: formatted lyrics and coverage score for user input
    """
    nb_lines = lyrics.count("\\n")
    user_progress = nb_found_words / nb_total_words
    nb_to_show = int(nb_lines * user_progress) + 1
    raw_selected_lyrics = "\\n".join(lyrics.split("\\n")[:nb_to_show])
    return extract_and_format_lyrics(raw_selected_lyrics), int(user_progress * 100)


def remove_multiple_strings(text: str, to_remove: list[str]):
    """Removes multiple strings from a text.

    Args:
        text (str): raw text to clean
        to_remove (list[str]): list of strings to remove

    Returns:
        str: text with all listed strings removed
    """
    for string_to_remove in to_remove:
        text = text.replace(string_to_remove, "")
    return text
