"""Static landing page moved out of app.py and registered from app startup.

This module exposes `attach(server)` which registers the `/tada` route
on the Flask `server` passed in. The HTML is stored in `_LANDING_PAGE_HTML`.
"""

from flask import render_template_string
import plotly.express as px
from dash import Dash, Input, Output, dcc, html
from pages.utils import return_cat_rankings_df

_LANDING_PAGE_HTML = """
                <!doctype html>
                <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>NOPLP stats - Statistiques N'oubliez pas les paroles</title>
                    <style>
                        :root {
                            color-scheme: light;
                            --bg: #0f172a;
                            --bg-soft: #111827;
                            --panel: rgba(15, 23, 42, 0.82);
                            --border: rgba(148, 163, 184, 0.25);
                            --text: #e5e7eb;
                            --muted: #94a3b8;
                            --accent: #f97316;
                            --accent-2: #38bdf8;
                        }
                        * { box-sizing: border-box; }
                        body {
                            margin: 0;
                            min-height: 100vh;
                            font-family: Inter, "Segoe UI", Roboto, sans-serif;
                            color: var(--text);
                            background:
                                radial-gradient(circle at top left, rgba(56, 189, 248, 0.18), transparent 32%),
                                radial-gradient(circle at top right, rgba(249, 115, 22, 0.18), transparent 30%),
                                linear-gradient(180deg, #020617 0%, var(--bg) 45%, var(--bg-soft) 100%);
                        }
                        .wrap {
                            max-width: 1120px;
                            margin: 0 auto;
                            padding: 40px 20px 56px;
                        }
                        .hero {
                            display: grid;
                            gap: 24px;
                            padding: 36px;
                            border: 1px solid var(--border);
                            border-radius: 28px;
                            background: var(--panel);
                            box-shadow: 0 24px 80px rgba(2, 6, 23, 0.45);
                            backdrop-filter: blur(14px);
                        }
                        .eyebrow {
                            margin: 0 0 10px;
                            color: var(--accent-2);
                            text-transform: uppercase;
                            letter-spacing: 0.14em;
                            font-size: 0.78rem;
                            font-weight: 700;
                        }
                        h1 {
                            margin: 0;
                            font-size: clamp(2.6rem, 5vw, 4.8rem);
                            line-height: 0.98;
                            max-width: 12ch;
                        }
                        .lede {
                            margin: 0;
                            max-width: 64ch;
                            color: var(--muted);
                            font-size: 1.05rem;
                            line-height: 1.7;
                        }
                        .actions {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 12px;
                        }
                        .pill {
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                            padding: 12px 18px;
                            border-radius: 999px;
                            text-decoration: none;
                            font-weight: 700;
                            border: 1px solid transparent;
                            transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
                        }
                        .pill:hover { transform: translateY(-1px); }
                        .pill.primary {
                            color: #0f172a;
                            background: linear-gradient(135deg, #f8fafc, #cbd5e1);
                        }
                        .pill.secondary {
                            color: var(--text);
                            border-color: var(--border);
                            background: rgba(15, 23, 42, 0.6);
                        }
                        .grid {
                            display: grid;
                            grid-template-columns: repeat(12, 1fr);
                            gap: 18px;
                            margin-top: 18px;
                        }
                        .card {
                            grid-column: span 4;
                            padding: 20px;
                            border-radius: 22px;
                            border: 1px solid var(--border);
                            background: rgba(15, 23, 42, 0.7);
                        }
                        .card h2 {
                            margin: 0 0 10px;
                            font-size: 1.05rem;
                        }
                        .card p {
                            margin: 0;
                            color: var(--muted);
                            line-height: 1.6;
                        }
                        .footer {
                            margin-top: 18px;
                            color: var(--muted);
                            font-size: 0.95rem;
                        }
                        @media (max-width: 900px) {
                            .card { grid-column: span 6; }
                        }
                        @media (max-width: 640px) {
                            .wrap { padding: 16px; }
                            .hero { padding: 22px; border-radius: 22px; }
                            .card { grid-column: span 12; }
                            .pill { width: 100%; }
                        }
                    </style>
                </head>
                <body>
                    <main class="wrap">
                        <section class="hero">
                            <div>
                                <p class="eyebrow">NOPLP stats</p>
                                <h1>Statistiques rapides sur N'oubliez pas les paroles</h1>
                            </div>
                            <p class="lede">
                                Explorez les chansons les plus populaires, les catégories, les interprètes et l'entraînement.
                                Cette page d'accueil est servie directement par Flask pour éviter l'écran de chargement initial de Dash.
                            </p>
                            <div class="actions">
                                <a class="pill primary" href="/global">Voir les statistiques globales</a>
                                <a class="pill secondary" href="/training">Commencer l'entraînement</a>
                            </div>
                        </section>

                        <section class="grid" aria-label="Navigation principale">
                            <article class="card">
                                <h2>Global</h2>
                                <p>Classements, couverture des catégories et fenêtre temporelle configurable.</p>
                            </article>
                            <article class="card">
                                <h2>Par catégorie</h2>
                                <p>Filtrez les chansons selon les points, la catégorie et la période sélectionnée.</p>
                            </article>
                            <article class="card">
                                <h2>Par chanson et interprète</h2>
                                <p>Consultez les apparitions, les classements et les paroles détaillées.</p>
                            </article>
                        </section>

                        <p class="footer">
                            Accès direct aux pages interactives: <a href="/global">Global</a>, <a href="/category">Par catégorie</a>, <a href="/song">Par chanson</a>, <a href="/singer">Par interprète</a>, <a href="/training">Entraînement</a>.
                        </p>
                    </main>
                </body>
                </html>
                """


def attach(server):
    """Register the `/tada` route and embed a small Dash app into the page.

    The Dash app is mounted under `/tada/dash/` and its minimized `index_string`
    is included into the Flask-rendered template via `dash_app.index()`.
    """

    # Create embedded Dash app mounted on the provided Flask server
    dash_app = Dash(
        __name__,
        server=server,
        routes_pathname_prefix="/tada/dash/",
        assets_folder="pages/assets",
        suppress_callback_exceptions=True,
    )

    # Minimal index_string so `dash_app.index()` returns only the entry+scripts
    dash_app.index_string = """{%app_entry%}{%config%}{%scripts%}{%renderer%}"""

    graph_df = return_cat_rankings_df()
    category_values = sorted(graph_df["category"].dropna().unique().tolist())
    rank_min = int(graph_df["rank"].min())
    rank_max = int(graph_df["rank"].max())

    # Interactive layout with category dropdown + rank range slider
    dash_app.layout = html.Div(
        [
            html.H4("Extrait interactif: couverture des catégories"),
            dcc.Dropdown(
                id="tada-category",
                options=[{"label": "Toutes les catégories", "value": "ALL"}]
                + [{"label": cat, "value": cat} for cat in category_values],
                value="ALL",
                clearable=False,
            ),
            html.Div("Plage de rangs", style={"marginTop": 12}),
            dcc.RangeSlider(
                id="tada-rank-range",
                min=rank_min,
                max=rank_max,
                value=[rank_min, min(rank_max, rank_min + 300)],
                step=1,
                allowCross=False,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
            dcc.Graph(id="tada-coverage"),
        ]
    )

    @dash_app.callback(
        Output("tada-coverage", "figure"),
        Input("tada-category", "value"),
        Input("tada-rank-range", "value"),
    )
    def _update_tada_coverage(selected_category, rank_range):
        low_rank, high_rank = rank_range
        filtered = graph_df[
            (graph_df["rank"] >= low_rank) & (graph_df["rank"] <= high_rank)
        ]
        if selected_category and selected_category != "ALL":
            filtered = filtered[filtered["category"] == selected_category]

        fig = px.line(
            data_frame=filtered,
            x="rank",
            y="coverage",
            color="category",
            hover_data={"name": True, "rank": True, "coverage": True, "category": True},
        )
        fig.update_layout(
            height=520,
            xaxis={"title": "Nombre de chansons à connaître"},
            yaxis={"title": "Pourcentage de couverture d'une catégorie"},
            legend={"title": {"text": "Catégorie"}},
        )
        return fig

    @server.route("/tada")
    def _tada():
        # Inject the Dash app HTML where desired inside the landing template.
        dash_html = dash_app.index()
        return render_template_string(
            _LANDING_PAGE_HTML.replace(
                '</section>\n\n                        <p class="footer">',
                "</section>\n\n                        <!-- Embedded Dash app -->\n                        "
                + dash_html
                + '\n\n                        <p class="footer">',
            )
        )
