"""Home page Dash app - standalone app with server=False for Flask integration"""

import dash

from pages.bootstrap import BOOTSTRAP_CSS

# Import the layout function from home.py
from pages.home import get_home_layout


def create_home_dash(server=None):
    """Create home page Dash app

    Args:
        server (Flask or None): Flask server instance, or None for standalone use.

    Returns:
        Dash app instance with server=False for blueprint integration
    """
    home_dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/",
        suppress_callback_exceptions=True,
        external_stylesheets=[BOOTSTRAP_CSS],
    )

    # Set the layout
    home_dash_app.layout = get_home_layout()

    return home_dash_app


# Create the Dash app with server=False for Flask integration
dash_app = create_home_dash(server=False)
