"""Main Flask application for noplp-stats

This is the main website. Dash apps are initialized with server=False
and registered as blueprints within this Flask app.
"""

import os
from flask import Flask, render_template

from pages.bootstrap import BOOTSTRAP_CSS, BOOTSTRAP_JS
from pages.global_stats import create_global_dash

server = Flask(__name__, template_folder="pages/templates", static_folder="pages/assets")
server.config["SUPPRESS_CALLBACK_EXCEPTIONS"] = True

global_page_dash = create_global_dash(server=server)

dash_apps = [global_page_dash]


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
    return render_template("home.html", title="Accueil")


@server.route("/global")
def global_stats():
    """Global statistics page served by Dash."""
    return render_template("dash_page_import.html", app_dash=global_page_dash.index())


@server.route("/category")
def category():
    """Category statistics page"""
    return render_template("dash_page.html", title="Par catégorie")


@server.route("/song")
def song():
    """Song statistics page"""
    return render_template("dash_page.html", title="Par chanson")


@server.route("/singer")
def singer():
    """Singer statistics page"""
    return render_template("dash_page.html", title="Par interprète")


@server.route("/training")
def training():
    """Training page"""
    return render_template("dash_page.html", title="Entraînement")


if __name__ == "__main__":
    if bool(os.getenv("DASH_DEBUG", None)):
        for app_dash in dash_apps:
            app_dash.enable_dev_tools(debug=True, dev_tools_ui=True)
    server.run(port=8080, debug=bool(os.getenv("DASH_DEBUG", None)))
