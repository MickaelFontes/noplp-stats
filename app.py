"""Main Flask application for noplp-stats

This is the main website. Dash apps are initialized with server=False
and registered as blueprints within this Flask app.
"""

import os
from flask import Flask, render_template

from pages.bootstrap import BOOTSTRAP_CSS, BOOTSTRAP_JS
from pages.global_dash import create_global_dash

# Create Flask app
app = Flask(__name__, template_folder="pages/templates", static_folder="pages/assets")
app.config["SUPPRESS_CALLBACK_EXCEPTIONS"] = True

global_page_dash = create_global_dash(
    server=app
)  # Initialize the global Dash app with the Flask server


@app.context_processor
def inject_bootstrap_assets():
    """Expose shared Bootstrap assets to Jinja templates."""
    return {
        "bootstrap_css": BOOTSTRAP_CSS,
        "bootstrap_js": BOOTSTRAP_JS,
    }


@app.route("/")
def home():
    """Home page - Flask template with embedded Dash app"""
    return render_template("home.html", title="Accueil")


@app.route("/global")
def global_stats():
    """Global statistics page served by Dash."""
    return global_page_dash.index()


@app.route("/category")
def category():
    """Category statistics page"""
    return render_template("dash_page.html", title="Par catégorie")


@app.route("/song")
def song():
    """Song statistics page"""
    return render_template("dash_page.html", title="Par chanson")


@app.route("/singer")
def singer():
    """Singer statistics page"""
    return render_template("dash_page.html", title="Par interprète")


@app.route("/training")
def training():
    """Training page"""
    return render_template("dash_page.html", title="Entraînement")


app.debug = bool(os.getenv("DASH_DEBUG", None))


if __name__ == "__main__":
    app.run(port=8080, debug=bool(os.getenv("DASH_DEBUG", None)))
