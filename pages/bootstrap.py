"""Shared Bootstrap assets for Flask templates and Dash apps."""

import dash_bootstrap_components as dbc

BOOTSTRAP_VERSION = "5.3.6"

BOOTSTRAP_CSS = {
    "href": dbc.themes.BOOTSTRAP,
    "rel": "stylesheet",
    "integrity": "sha256-oxqX0LQclbvrsJt8IymkxnISn4Np2Wy2rY9jjoQlDEg=",
    "crossorigin": "anonymous",
}

BOOTSTRAP_JS = {
    "src": f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js",
    "integrity": "sha384-j1CDi7MgGQ12Z7Qab0qlWQ/Qqz24Gc6BM0thvEMVjHnfYGF0rmFCozFSxQBxwHKO",
    "crossorigin": "anonymous",
}
