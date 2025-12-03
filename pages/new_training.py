"""Training page to guess songs lyrics, step-by-step interactive version."""

import json
import re
from datetime import datetime
from urllib.parse import unquote

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback, html, dcc
from pages.utils import DEFAULT_SONG, get_song_dropdown_menu, return_lyrics_df, song_exists

PAGE_PATH = "/new-training"

dash.register_page(__name__, path=PAGE_PATH, path_template=PAGE_PATH+"/<song_title>",
                   title="Entraînement - NOLPL stats")


# Update layout to accept song_title
def layout(song_title="2 be 3", **_):
    song_title = unquote(song_title)
    return dbc.Container([
        dcc.Location(id="url-training", refresh=False),
        html.H5("Zone d'entraînement pour apprendre les paroles"),
        html.P("Choisissez une chanson et devinez les paroles ligne par ligne !"),
        get_song_dropdown_menu(song_title, component_id="dropdown-song-new-training"),
        html.Hr(),
        dcc.Store(id="training-state", data={}),
        dcc.Store(id="user-training-stats", storage_type="local"),  # New store for stats
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
        return " ".join(
            [w if w.endswith("'") and len(w) == 2 else w[0] + ("_" * 4) if len(w) > 1 else w for w in split_words]
        )
    return " ".join(["_" * 4 for w in split_words])


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
        html.Div([dbc.Button("Suivant", id={"type": "reveal-btn", "index": step}, n_clicks=0,
                 color="primary", className="mt-3")], className="d-flex justify-content-center"),
    ], body=True)


def render_guess_line(lines, step, shown, state):
    """Render the guessing line (masked or revealed)."""
    idx = get_guess_indices(lines)[step - shown]
    line = lines[idx]
    display_line = line.lstrip("¤").strip() if line.startswith("¤") else line
    style = {"fontWeight": "bold"} if line.startswith("¤") else {}
    # Back button available when we're past the initial shown lines
    can_go_back = step > shown

    if not state.get("revealed"):
        masked = mask_line(display_line, state.get("show_first_letter", False))
        right_btns = []
        if not state.get("show_first_letter"):
            right_btns.append(
                dbc.Button(
                    "Initiales",
                    id={"type": "first-letter-btn", "index": step},
                    n_clicks=0, color="secondary", className="me-2"
                )
            )
        right_btns.append(
            dbc.Button(
                "Montrer la ligne",
                id={"type": "reveal-btn", "index": step},
                n_clicks=0,
                color="primary",
            )
        )

        left = []
        if can_go_back:
            left.append(dbc.Button(
                "<-",
                id={"type": "back-btn", "index": step},
                n_clicks=0, color="secondary",
            ))

        return dbc.Card([
            html.H2(masked, style=style),
            html.Div([
                html.Div(left, className="d-flex"),
                html.Div(right_btns, className="d-flex justify-content-end"),
            ], className="mt-3 d-flex justify-content-between flex-wrap gap-2 align-items-center"),
        ], body=True)

    # revealed state: show full line and answer buttons, with back on left
    left = []
    if can_go_back:
        left.append(dbc.Button(
            "<-",
            id={"type": "back-btn", "index": step},
            n_clicks=0, color="secondary",
        ))

    return dbc.Card([
        html.H2(display_line, style=style),
        html.Div([
            html.Div(left, className="d-flex"),
            html.Div([
                dbc.Button(
                    "Non",
                    id={"type": "dont-know-btn", "index": step},
                    n_clicks=0,
                    color="danger",
                    className="me-2 flex-shrink-0",
                ),
                dbc.Button(
                    "Oui",
                    id={"type": "know-btn", "index": step},
                    n_clicks=0,
                    color="success",
                    className="flex-shrink-0",
                ),
            ], className="d-flex justify-content-end"),
        ], className="mt-3 d-flex justify-content-between flex-wrap gap-2 align-items-center"),
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
    Input("dropdown-song-new-training", "value"),
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
    # --- Save training stats to localStorage ---
    # Use dcc.Store to trigger a clientside callback to persist stats
    # We'll add a new dcc.Store for stats and update it here
    return state, render_final(lines, state)


# --- Step action callback ---
def _apply_guessing_actions(state, *, step_val, first_letter, reveal, know, dont_know):
    """Apply guessing-stage interactions to the state and return it.

    Interaction flags are keyword-only to avoid too-many-positional-arguments
    pylint warnings while keeping call sites explicit.
    """
    if first_letter and any(first_letter):
        state["show_first_letter"] = True
    if reveal and any(reveal):
        state["revealed"] = True
    if know and any(know):
        state.setdefault("results", []).append(True)
        state["step"] = step_val + 1
        state["show_first_letter"] = False
        state["revealed"] = False
    if dont_know and any(dont_know):
        state.setdefault("results", []).append(False)
        state["step"] = step_val + 1
        state["show_first_letter"] = False
        state["revealed"] = False
    return state


def _handle_back_action(state, step_val, shown, back):
    """Handle back button action. Returns (state, handled_bool)."""
    if back and any(back):
        if step_val > shown:
            state["step"] = step_val - 1
            if (results := state.get("results", [])):
                results.pop()
                state["results"] = results
            state["show_first_letter"] = False
            # When going back to the previous guessed line, show it revealed
            state["revealed"] = True
            state["finished"] = False
        elif step_val > 0:
            state["step"] = step_val - 1
        return state, True
    return state, False


def _handle_forward_interactions(state, step_val, shown, *, reveal, first_letter, know, dont_know):
    """Handle forward interactions (intro and guessing stage)."""
    if step_val < shown:
        if reveal and any(reveal):
            state["step"] = step_val + 1
        return state
    return _apply_guessing_actions(
        state,
        step_val=step_val,
        first_letter=first_letter,
        reveal=reveal,
        know=know,
        dont_know=dont_know,
    )


def _parse_trigger_json(s):
    """Parse a JSON-like trigger identifier and return (type, index).

    Accepts either a dict (already parsed) or a JSON string. Returns
    (None, None) when parsing fails or when the data is not present.
    """
    if isinstance(s, dict):
        return s.get("type"), s.get("index")
    if not isinstance(s, str):
        return None, None
    try:
        parsed = json.loads(s)
    except json.JSONDecodeError:
        return None, None
    if isinstance(parsed, dict):
        return parsed.get("type"), parsed.get("index")
    return None, None


def _get_trigger_info():
    """Return (type, index) for the triggering Dash input or (None, None).

    This helper centralizes detection of which pattern-matching button
    triggered a callback. It prefers `dash.ctx.triggered_id` (newer
    Dash versions) and falls back to parsing `dash.callback_context.triggered`.

    Returns:
    - (type: str, index: int) when detected
    - (None, None) when no valid trigger could be parsed
    """
    ctx = dash.callback_context
    tid = dash.ctx.triggered_id

    if isinstance(tid, dict):
        return tid.get("type"), tid.get("index")
    # Try parsing `tid` or fallback to `callback_context.triggered` prop
    t_type, t_index = _parse_trigger_json(tid)
    if t_type is not None:
        return t_type, t_index

    if not (triggered := ctx.triggered):
        return None, None

    prop = triggered[0]["prop_id"].split(".")[0]
    return _parse_trigger_json(prop)


@callback(
    output=Output("training-state", "data", allow_duplicate=True),
    inputs={"reveal": Input({"type": "reveal-btn", "index": dash.ALL}, "n_clicks"),
            "first_letter": Input({"type": "first-letter-btn", "index": dash.ALL}, "n_clicks"),
            "know": Input({"type": "know-btn", "index": dash.ALL}, "n_clicks"),
            "dont_know": Input({"type": "dont-know-btn", "index": dash.ALL}, "n_clicks"),
            "back": Input({"type": "back-btn", "index": dash.ALL}, "n_clicks"), },
    state={"training_state": State("training-state", "data")},
    prevent_initial_call=True,
)
def step_action(*, reveal, first_letter, know, dont_know, back, training_state):
    """Handle a single user interaction and update training state.

    The page uses pattern-matching IDs for buttons, so each input arrives as
    a list of `n_clicks` values (one per existing button). Rapid user clicks
    or delayed UI updates can leave stale values in these lists that do not
    correspond to the line currently displayed. To prevent skipping or
    applying actions intended for another line, this callback:

    - determines which input actually triggered the callback and its
      `index` using `_get_trigger_info()`;
    - ignores the event when the triggered `index` doesn't match the
      current `step` shown to the user;
    - treats `back-btn` specially (may remove a previous result and set
      the previous line as revealed);
    - delegates forward actions (reveal, initial letters, know/don't-know)
      to `_handle_forward_interactions` which applies them to the state.

    Parameters (kwargs provided by Dash):
    - `reveal`, `first_letter`, `know`, `dont_know`, `back`: lists of
      `n_clicks` for each pattern-matching input type.
    - `training_state`: dict stored in `dcc.Store(id="training-state")`.

    Returns:
    - updated `training_state` dict that Dash will write back to the store.
    """
    # Defensive defaults
    training_state = training_state or {}
    lines = training_state.get("lines", [])
    non_empty_indices = get_non_empty_indices(lines)
    shown = min(3, len(non_empty_indices))
    step_val = training_state.get("step", 0)

    t_type, t_index = _get_trigger_info()
    if t_type is None:
        return training_state

    # Ignore clicks that came from a button not matching the displayed step.
    if t_index != step_val:
        return training_state

    # Back button handled specially (it may modify previous results).
    if t_type == "back-btn":
        training_state, handled = _handle_back_action(training_state, step_val, shown, back)
        if handled:
            return training_state
        return training_state

    # Forward interactions (intro or guessing) — reuse the raw payloads
    # provided by Dash. Because we confirmed the trigger's index matches
    # `step_val`, it's safe to process the inputs as-is.
    return _handle_forward_interactions(
        training_state,
        step_val,
        shown,
        reveal=reveal,
        first_letter=first_letter,
        know=know,
        dont_know=dont_know,
    )


# --- Save stats callback ---
@callback(
    Output("user-training-stats", "data", allow_duplicate=True),
    Input("training-state", "data"),
    State("user-training-stats", "data"),
    prevent_initial_call=True,
)
def save_training_stats(state, stats):
    if not state.get("finished"):
        return dash.no_update
    if not state.get("song_title") or not state.get("lines") or not state.get("results"):
        return dash.no_update
    # Find line numbers where user clicked 'no'
    guess_indices = get_guess_indices(state["lines"])
    guessed_lines = {line: state["results"][i] for i, line in enumerate(guess_indices)}
    # Compose training record
    record = {
        "song_title": state["song_title"],
        "timestamp": datetime.now(),
        "guessed_lines": guessed_lines,
    }
    # Append to stats
    stats = stats or []
    stats.append(record)
    return stats


# --- URL update callback ---
@callback(
    Output("url-training", "pathname"),
    Output("dropdown-song-new-training", "value"),
    Input("dropdown-song-new-training", "value"),
    Input("url-training", "pathname"),
)
def update_url_from_dropdown(song_title, url_pathname):
    len_training_prefix = len(PAGE_PATH)
    if url_pathname[:len_training_prefix] == PAGE_PATH:
        param = unquote(url_pathname)[len_training_prefix + 1:]
        if param and not song_exists(param):
            return f"{PAGE_PATH}/{DEFAULT_SONG}", DEFAULT_SONG
        if param == song_title:
            return dash.no_update, dash.no_update
        training_url = f"{PAGE_PATH}/{song_title}"
        return training_url, dash.no_update
    return dash.no_update, dash.no_update
