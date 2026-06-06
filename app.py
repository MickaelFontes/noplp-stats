"""Main Flask application for noplp-stats

This is the main website. Dash apps are initialized with server=False
and registered as blueprints within this Flask app.
"""

import os
from flask import Flask, render_template, request
import dash
from pages.bootstrap import BOOTSTRAP_CSS, BOOTSTRAP_JS

server = Flask(
    __name__, template_folder="pages/templates", static_folder="pages/assets"
)

app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname="/",
    index_string="{%app_entry%}\n{%config%}\n{%scripts%}\n{%renderer%}",
    suppress_callback_exceptions=True,
    use_pages=True,
    update_title=None
)


@server.context_processor
def inject_bootstrap_assets():
    """Expose shared Bootstrap assets to Jinja templates."""
    return {
        "bootstrap_css": BOOTSTRAP_CSS,
        "bootstrap_js": BOOTSTRAP_JS,
    }

@server.route("/")
def home():
    """Home page - Flask template with embedded Dash app"""
    return render_template("home.html")

@server.before_request
@server.route("/")
def redirect_conflicting_paths():
    """Home page - Flask template with embedded Dash app"""
    if request.method == "GET" and request.path == "/":
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
    return render_template("dash_page_import.html", title="Par catégorie", app_dash=app.index())

@server.route("/song/<song_title>")
@server.route("/song")
def song(song_title=None, **_):
    """Song statistics page"""
    return render_template("dash_page_import.html", title=song_title if song_title else "Par chanson", app_dash=app.index())

@server.route("/singer/<singer_name>")
@server.route("/singer")
def singer(singer_name=None, **_):
    """Singer statistics page"""
    return render_template("dash_page_import.html", title=singer_name if singer_name else "Par interprète", app_dash=app.index())


@server.route("/training/type")
@server.route("/training/type/<song_title>")
def training_type(song_title=None, **_):
    """Training type selection page"""
    return render_template("dash_page_import.html", title=song_title if song_title else "Entraînement clavier", app_dash=app.index())


@server.route("/training/yes_no")
@server.route("/training/yes_no/<song_title>")
def training_yes_no(song_title=None, **_):
    """Training yes/no page"""
    return render_template("dash_page_import.html", title=song_title if song_title else "Entraînement oui/non", app_dash=app.index())


@server.route("/training")
def training():
    """Training page"""
    return render_template("training.html", title="Entraînement")



@server.route("/about")
def about():
    """About page"""
    return render_template("about.html")

if __name__ == "__main__":
    if bool(os.getenv("DASH_DEBUG", None)):
        app.enable_dev_tools(debug=True, dev_tools_ui=True)
    server.run(port=8080, debug=bool(os.getenv("DASH_DEBUG", None)))
