"""Bottom of the pages."""
import os
from dash import dcc, html

bottom = html.Div(
    [
        html.Hr(),
        dcc.Markdown(
            [
                "NOLPL Stats - Paroles et données issues du ",
                "[Fandom NOPLP](https://n-oubliez-pas-les-paroles.fandom.com/fr/wiki/Wiki_N%27oubliez_pas_les_paroles) ",
                "sous ![CC icon](assets/images/cc-by-sa-3.svg#thumbnail) ",
                "[CC-BY_SA](https://creativecommons.org/licenses/by-sa/3.0/deed.fr) - ",
                "Exploitation et visualisation en open source sur",
                " ![Github](https://github.githubassets.com/favicons/favicon.svg#thumbnail) ",
                "[noplp-stats](https://github.com/MickaelFontes/noplp-stats) sous ",
                "[MIT License](https://github.com/MickaelFontes/noplp-stats/blob/main/LICENSE) - ",  # noqa: E501
                "Dernière mise à jour: le " + os.environ.get("LAST_UPDATE"),
            ]
        ),
    ],
    style={"textAlign": "center", "marginBottom": 20},
)
