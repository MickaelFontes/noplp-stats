"""Main Flask application for noplp-stats

This is the main website. Dash apps are initialized with server=False
and registered as blueprints within this Flask app.
"""

import os
from flask import Flask, render_template

from pages.bootstrap import BOOTSTRAP_CSS, BOOTSTRAP_JS

# Create Flask app
app = Flask(__name__, template_folder="pages/templates", static_folder="pages/assets")
app.config["SUPPRESS_CALLBACK_EXCEPTIONS"] = True


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
    """Global statistics page"""
    return render_template("dash_page.html", title="Global")


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


# Register Dash apps as blueprints
# Dash apps are initialized with server=False and integrated via blueprints
# Dash apps will be registered here once they are created:
# from pages.home_dash import dash_app as home_dash_app
# app.register_blueprint(home_dash_app.server)


# Enable debug mode via environment variable
app.debug = bool(os.getenv("DASH_DEBUG", None))


if __name__ == "__main__":
    app.run(port=8080, debug=bool(os.getenv("DASH_DEBUG", None)))
