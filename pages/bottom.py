"""Bottom of the pages."""
from dash import dcc, html

bottom = html.Div(
    [
        html.Hr(),
        dcc.Markdown(
            "NOLPL Stats - Paroles et données issues du [Fandom NOPLP](https://n-oubliez-pas-les-paroles.fandom.com/fr/wiki/Wiki_N%27oubliez_pas_les_paroles) sous ![CC icon](https://creativecommons.org/favicon.ico) [CC-BY_SA](https://creativecommons.org/licenses/by-sa/3.0/deed.fr) - Exploitation et visualisation en open source sur ![Github](https://github.githubassets.com/favicons/favicon.svg) [noplp-stats](https://github.com/MickaelFontes/noplp-stats) sous [MIT License](https://github.com/MickaelFontes/noplp-stats/blob/main/LICENSE)"  # noqa: E501
        ),
    ],
    style={"textAlign": "center", "marginBottom": 20},
)
