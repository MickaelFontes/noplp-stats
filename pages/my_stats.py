"""My Stats page: shows user's training history and scores."""
from collections import defaultdict, Counter

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, callback, ctx
from dash.dependencies import ALL
from pages.utils import return_lyrics_df


dash.register_page(__name__, path="/my-stats", title="Mes stats - NOLPL stats")


layout = dbc.Container([
    html.H5("Mes stats d'entraînement"),
    html.P("Retrouvez vos 10 dernières chansons entraînées, recherchez d'autres, et consultez vos scores !"),
    dcc.Store(id="user-training-stats", storage_type="local"),
    dcc.Store(id="selected-song", data={"title": None, "open": False}),  # Store for selected song and open state
    dcc.Input(id="search-song", type="text", placeholder="Rechercher une chanson...", className="mb-3"),
    html.Div(id="recent-songs"),
    # Removed my_stats_song_details card from layout
], style={"marginTop": 20})

# --- Helper functions ---


def compute_song_scores(stats):
    """Return dict: song_title -> list of scores (percent known lines)."""
    song_scores = defaultdict(list)
    for rec in stats:
        if rec.get("total"):
            score = sum(rec["results"]) / rec["total"] * 100
            song_scores[rec["song_title"].strip()].append(score)
    return song_scores


def get_last_n_unique(stats, n=10):
    """Return last n unique song training records, most recent first."""
    seen = set()
    unique = []
    for rec in sorted(stats, key=lambda r: r["timestamp"], reverse=True):
        title = rec["song_title"]
        if title not in seen:
            seen.add(title)
            unique.append(rec)
        if len(unique) == n:
            break
    return unique


def get_line_mistakes(song_title, stats):
    """Return Counter of mistakes per line for a song."""
    line_mistakes = Counter()
    for rec in stats:
        if rec["song_title"] == song_title:
            for line in rec["mistakes"]:
                line_mistakes[line] += 1
    return line_mistakes


def get_lyrics_lines(song_title):
    """Return lyrics lines for a song, or None if not found."""
    lyrics_df = return_lyrics_df()
    lyrics_row = lyrics_df[lyrics_df["name"] == song_title]
    if lyrics_row.empty:
        return None
    return lyrics_row["lyrics"].values[0].split("\\n")


def render_lyrics(lines, line_mistakes):
    """Return list of html elements for lyrics with color gradation."""
    if not lines:
        return [html.P("Paroles non disponibles.")]
    max_mistakes = max(line_mistakes.values()) if line_mistakes else 1

    def get_color(count):
        if count == 0:
            return {}
        ratio = count / max_mistakes
        r, g, b = 255, int(255 * (1 - ratio)), 0
        return {"backgroundColor": f"rgb({r},{g},{b})"}

    children = []
    for i, line in enumerate(lines):
        style = get_color(line_mistakes[i])
        if line.startswith("¤"):
            style["fontWeight"] = "bold"
            display_line = line.lstrip("¤").strip()
        else:
            display_line = line.strip()
        children.append(html.Br() if line.strip() == "" else html.Div(display_line, style=style))
    return children


def render_song_card(title, min_score, is_open, stats):
    """Render a song card with collapsible lyrics details."""
    line_mistakes = get_line_mistakes(title, stats)
    lines = get_lyrics_lines(title)
    details = dbc.Collapse(
        dbc.Card([
            html.H4(f"Détails pour {title}"),
            html.Div(render_lyrics(lines, line_mistakes)),
        ], body=True),
        is_open=is_open,
        className="mt-2"
    ) if is_open else dbc.Collapse([], is_open=False)
    return dbc.Card([
        html.H5(title),
        html.P(f"Score (minimum des 3 derniers): {min_score:.1f}%"),
        dbc.Button("Voir détails", id={"type": "show-details", "index": title}, n_clicks=0),
        details,
    ], body=True, className="mb-2")


# --- Main callback ---

@callback(
    Output("recent-songs", "children"),
    Output("selected-song", "data"),
    Input("user-training-stats", "data"),
    Input("search-song", "value"),
    Input({"type": "show-details", "index": ALL}, "n_clicks"),
    State("selected-song", "data"),
)
def show_stats(stats, search, n_clicks_list, selected_song):
    if not stats:
        return "Aucun entraînement enregistré.", {"title": None, "open": False}
    song_scores = compute_song_scores(stats)
    filtered = [rec for rec in stats if not search or search.lower() in rec["song_title"].lower()]
    recent = get_last_n_unique(filtered, 10)
    triggered = ctx.triggered_id
    prev_title = selected_song.get("title") if selected_song else None
    prev_open = selected_song.get("open") if selected_song else False
    new_title = prev_title
    new_open = prev_open
    if triggered and isinstance(triggered, dict) and triggered.get("type") == "show-details":
        clicked_title = triggered.get("index")
        if clicked_title == prev_title:
            new_open = not prev_open  # Toggle
        else:
            new_title = clicked_title
            new_open = True
    cards = []
    for rec in recent:
        title = rec["song_title"]
        scores = song_scores[title][-3:]
        min_score = min(scores) if scores else 0
        is_open = (title == new_title and new_open)
        cards.append(render_song_card(title, min_score, is_open, stats))
    return cards, {"title": new_title, "open": new_open}
