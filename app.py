"""Main Flask application for noplp-stats

This is the main website. Dash apps are initialized with server=False
and registered as blueprints within this Flask app.
"""

import os
from flask import Flask, redirect, render_template, request, url_for, send_file
import dash
from pages.bootstrap import BOOTSTRAP_CSS, BOOTSTRAP_JS

server = Flask(
    __name__, template_folder="pages/templates", static_folder="pages/assets"
)


def do_not_register_catch_all(func):
    """We want to avoid Dash catch-all responses with HTTP 200
    Even for paths not registered.
    """

    def wrapper(*args, **kwargs):
        if "<path:path>" in args:
            return None
        result = func(*args, **kwargs)
        return result

    return wrapper


dash.Dash._add_url = do_not_register_catch_all(dash.Dash._add_url)

app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname="/",
    index_string="{%app_entry%}\n{%config%}\n{%scripts%}\n{%renderer%}",
    suppress_callback_exceptions=True,
    use_pages=True,
    update_title=None,
)


@server.context_processor
def inject_bootstrap_assets():
    """Expose shared Bootstrap assets to Jinja templates."""
    return {
        "bootstrap_css": BOOTSTRAP_CSS,
        "bootstrap_js": BOOTSTRAP_JS,
    }


@server.before_request
def redirect_conflicting_paths():
    """Home page redirection - To override Dash redirection for "/" path"""
    if request.method == "GET" and request.path == "/":
        return render_template("home.html")
    return None


@server.route("/favicon.ico")
def favicon():
    """Serve the favicon.ico file."""
    return send_file(
        os.path.join(server.static_folder, "images/noplp-stats-argent-logo.ico"),
        mimetype="image/x-icon",
    )


@server.route("/")
def home():
    """Home page - Flask template only"""
    return render_template("home.html")


@server.route("/global")
def global_stats():
    """Global statistics page served by Dash."""
    return render_template(
        "dash_page_import.html", title="Global", app_dash=app.index()
    )


@server.route("/category")
def category():
    """Category statistics page"""
    return render_template(
        "dash_page_import.html", title="Par catégorie", app_dash=app.index()
    )


@server.route("/song/<song_title>")
@server.route("/song")
def song(song_title=None, **_):
    """Song statistics page"""
    return render_template(
        "dash_page_import.html",
        title=song_title if song_title else "Par chanson",
        app_dash=app.index(),
    )


@server.route("/singer/<singer_name>")
@server.route("/singer")
def singer(singer_name=None, **_):
    """Singer statistics page"""
    return render_template(
        "dash_page_import.html",
        title=singer_name if singer_name else "Par interprète",
        app_dash=app.index(),
    )


@server.route("/training/type")
@server.route("/training/type/<song_title>")
def training_type(song_title=None, **_):
    """Training type selection page"""
    return render_template(
        "dash_page_import.html",
        title=(
            song_title + " - Entraînement clavier"
            if song_title
            else "Entraînement clavier"
        ),
        app_dash=app.index(),
    )


@server.route("/new-training/<song_title>")
def legacy_new_training(song_title):
    return redirect(url_for("training_yes_no", song_title=song_title))


@server.route("/training/yes_no")
@server.route("/training/yes_no/<song_title>")
def training_yes_no(song_title=None, **_):
    """Training yes/no page"""
    return render_template(
        "dash_page_import.html",
        title=(
            song_title + " - Entraînement oui/non"
            if song_title
            else "Entraînement oui/non"
        ),
        app_dash=app.index(),
    )


@server.route("/training")
def training():
    """Training page"""
    return render_template("training.html", title="Entraînement")


@server.route("/about")
def about():
    """About page"""
    return render_template(
        "dash_page_import.html",
        title="À propos",
        app_dash=app.index(),
    )


if __name__ == "__main__":
    if bool(os.getenv("DASH_DEBUG", None)):
        app.enable_dev_tools(debug=True, dev_tools_ui=True)
    server.run(port=8080, debug=bool(os.getenv("DASH_DEBUG", None)))
