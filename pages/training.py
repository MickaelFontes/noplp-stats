"""Training page to guess songs lyrics, step-by-step interactive version."""

import re
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html, dcc
from pages.utils import get_song_dropdown_menu, return_lyrics_df

dash.register_page(__name__, path="/training", title="Entraînement - NOLPL stats")

layout = dbc.Container([
    html.H5("Zone d'entraînement pour apprendre les paroles"),
    html.P("Choisissez une chanson et devinez les paroles ligne par ligne !"),
    get_song_dropdown_menu(),
    html.Hr(),
    dcc.Store(id="training-state", data={}),
    html.Div(id="training-step"),
], style={"marginTop": 20})

# --- Helper functions ---


def get_lyrics_lines(song_title):
    """Return lyrics as a list of lines, preserving empty lines."""
    lyrics_df = return_lyrics_df()
    raw_lyrics = lyrics_df[lyrics_df["name"] == song_title]["lyrics"].values[0]
    return raw_lyrics.split("\\n")


def mask_line(line, show_first_letter=False):
    """Mask words in a line, splitting contractions for French lyrics."""
    # Split on spaces and apostrophes followed by a letter (e.g. s'est -> s' est)
    words = re.findall(r"\b\w+'|\w+|\w+'\w+|\w+'", line)
    split_words = []
    for w in words:
        if re.match(r"^\w+'\w+", w):
            parts = re.split(r"(')", w)
            if len(parts) >= 3:
                split_words.append(parts[0] + parts[1])
                split_words.append(parts[2])
            else:
                split_words.append(w)
        else:
            split_words.append(w)
    if show_first_letter:
        return " ".join([w if w.endswith("'") else w[0] + ("_" * (len(w) - 1)) if len(w) > 1 else w for w in split_words])
    return " ".join(["_" * len(w) for w in split_words])


def get_non_empty_indices(lines):
    """Return indices of non-empty lines."""
    return [i for i, line in enumerate(lines) if line.strip()]


def get_guess_indices(lines):
    """Return indices of lines to guess (after first 3 non-empty lines)."""
    shown, idx = 0, 0
    while shown < 3 and idx < len(lines):
        if lines[idx].strip():
            shown += 1
        idx += 1
    return [i for i in range(idx, len(lines)) if lines[i].strip()]


def render_intro_line(lines, step):
    """Render the intro line (first 3 non-empty lines)."""
    idx = get_non_empty_indices(lines)[step]
    line = lines[idx]
    display_line = line.lstrip("¤").strip() if line.startswith("¤") else line
    style = {"fontWeight": "bold"} if line.startswith("¤") else {}
    return dbc.Card([
        html.H2(display_line, style=style),
        dbc.Button("Suivant", id={"type": "reveal-btn", "index": step}, n_clicks=0, color="primary", className="mt-3"),
    ], body=True)


def render_guess_line(lines, step, shown, state):
    """Render the guessing line (masked or revealed)."""
    idx = get_guess_indices(lines)[step - shown]
    line = lines[idx]
    display_line = line.lstrip("¤").strip() if line.startswith("¤") else line
    style = {"fontWeight": "bold"} if line.startswith("¤") else {}
    if not state.get("revealed"):
        masked = mask_line(display_line, state.get("show_first_letter", False))
        btns = []
        if not state.get("show_first_letter"):
            btns.append(
                dbc.Button(
                    "Montrer les initiales",
                    id={"type": "first-letter-btn", "index": step},
                    n_clicks=0, color="secondary", className="me-2"
                )
            )
        btns.append(dbc.Button("Montrer la ligne", id={"type": "reveal-btn", "index": step}, n_clicks=0, color="primary"))
        return dbc.Card([
            html.H2(masked, style=style),
            html.Div(btns, className="mt-3 d-flex justify-content-end"),
        ], body=True)
    return dbc.Card([
        html.H2(display_line, style=style),
        html.Div([
            dbc.Button("Non", id={"type": "dont-know-btn", "index": step}, n_clicks=0, color="danger", className="me-2"),
            dbc.Button("Oui", id={"type": "know-btn", "index": step}, n_clicks=0, color="success"),
        ], className="mt-3 d-flex justify-content-between"),
    ], body=True)


def render_final(lines, state):
    """Render the final lyrics with highlights."""
    guess_indices = get_guess_indices(lines)
    children, guessed_idx = [], 0
    for i, line in enumerate(lines):
        display_line = line.lstrip("¤").strip() if line.startswith("¤") else line
        style = {"fontWeight": "bold"} if line.startswith("¤") else {}
        if i in guess_indices and guessed_idx < len(state["results"]):
            if not state["results"][guessed_idx]:
                style["color"] = "red"
            guessed_idx += 1
        children.append(html.Br() if line.strip() == "" else html.Div(display_line, style=style))
    return dbc.Card([
        html.H4("Résultat final"),
        html.Div(children),
    ], body=True)


# --- Main callback ---
@callback(
    Output("training-state", "data"),
    Output("training-step", "children"),
    Input("dropdown-song", "value"),
    Input("training-state", "data"),
)
def training_step(song_title, state):
    if not state or state.get("song_title") != song_title:
        lines = get_lyrics_lines(song_title) if song_title else []
        state = {
            "song_title": song_title,
            "lines": lines,
            "step": 0,
            "show_first_letter": False,
            "revealed": False,
            "results": [],
            "finished": False,
        }
    if state.get("finished"):
        return state, render_final(state["lines"], state)
    step = state["step"]
    lines = state["lines"]
    non_empty_indices = get_non_empty_indices(lines)
    shown = min(3, len(non_empty_indices))
    if step < shown:
        return state, render_intro_line(lines, step)
    guess_indices = get_guess_indices(lines)
    while step - shown < len(guess_indices):
        idx = guess_indices[step - shown]
        if lines[idx].strip() == "":
            state["step"] += 1
            step = state["step"]
            continue
        return state, render_guess_line(lines, step, shown, state)
    state["finished"] = True
    return state, render_final(lines, state)


# --- Step action callback ---
@callback(
    Output("training-state", "data", allow_duplicate=True),
    Input({"type": "reveal-btn", "index": dash.ALL}, "n_clicks"),
    Input({"type": "first-letter-btn", "index": dash.ALL}, "n_clicks"),
    Input({"type": "know-btn", "index": dash.ALL}, "n_clicks"),
    Input({"type": "dont-know-btn", "index": dash.ALL}, "n_clicks"),
    State("training-state", "data"),
    prevent_initial_call=True,
)
def step_action(reveal, first_letter, know, dont_know, state):
    if state.get("step", 0) < 3:
        if reveal and any(reveal):
            state["step"] += 1
    else:
        if first_letter and any(first_letter):
            state["show_first_letter"] = True
        if reveal and any(reveal):
            state["revealed"] = True
        if know and any(know):
            state["results"].append(True)
            state["step"] += 1
            state["show_first_letter"] = False
            state["revealed"] = False
        if dont_know and any(dont_know):
            state["results"].append(False)
            state["step"] += 1
            state["show_first_letter"] = False
            state["revealed"] = False
    return state
