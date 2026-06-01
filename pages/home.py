"""Home page layout."""

import dash_bootstrap_components as dbc
from dash import html


def get_home_layout():
    """Return the home page layout.

    This layout is rendered when the home route is accessed.
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Présentation"),
                            html.P(
                                "Le but de cet outil est de présenter diverses statistiques sur les chansons demandées sur "
                                "l'émission N'oubliez pas les paroles. Elles peuvent être utilisées pour organiser ses "
                                "révisions, ou simplement pour satisfaire sa curiosité."
                            ),
                            html.P(
                                [
                                    html.Strong("NB:"),
                                    " Cette remarque s'applique à tout ce qui va suivre. ",
                                    html.Strong("Toutes"),
                                    " les données exploitées par ce site (paroles, apparitions des chansons, etc.) sont extraites "
                                    "du Fandom NOPLP. Elles peuvent être parfois incomplètes ou incorrectes. Ainsi, les statistiques "
                                    "affichées ici sont parfois inexactes puisque basées sur des données incomplètes. Malgré ces "
                                    "défauts, elles permettent quand-même d'extraire de précieuses informations.",
                                ]
                            ),
                        ],
                        md=8,
                    ),
                ],
                className="mt-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Fonctionnalités", className="mt-4"),
                            html.H3("Les statistiques"),
                            html.P(
                                "Pour cela, divers onglets de visualisation sont à votre disposition:"
                            ),
                            html.Ul(
                                [
                                    html.Li(
                                        [
                                            html.Strong("Global:"),
                                            " statistiques sur l'ensemble des chansons et des catégories, sur la fenêtre temporelle sélectionnée.",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Par catégorie:"),
                                            " statistiques spécifiques à chaque catégorie de l'émission (Même chanson, 50/40/... points, Maestro)",
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Par chanson:"),
                                            " toutes les informations relatives à une chanson:",
                                            html.Ul(
                                                [
                                                    html.Li(
                                                        "Nombre d'occurences par catégorie"
                                                    ),
                                                    html.Li(
                                                        "Classements selon son nombre d'apparitions"
                                                    ),
                                                    html.Li("Paroles"),
                                                ]
                                            ),
                                        ]
                                    ),
                                    html.Li(
                                        [
                                            html.Strong("Par interprète:"),
                                            " pour un.e interprète donné.e, affiche les chansons apparues dans l'émission et les statistiques correspondantes.",
                                        ]
                                    ),
                                ]
                            ),
                            html.H3("Entraînement", className="mt-3"),
                            html.P(
                                [
                                    "Cet onglet a pour but de vous aider à réviser une chanson ! Pour cela, vous devez taper ses "
                                    "paroles ",
                                    html.Strong("exactes"),
                                    " (comme dans l'émission) qui seront comparées à celles enregistrées sur le ",
                                    html.A(
                                        "Fandom NOPLP",
                                        href="https://n-oubliez-pas-les-paroles.fandom.com/fr/wiki/Wiki_N%27oubliez_pas_les_paroles",
                                        target="_blank",
                                    ),
                                    ".",
                                ]
                            ),
                            html.P(
                                "L'objectif est de taper toutes les paroles et ainsi remplir la barre de progression jusqu'au bout !"
                            ),
                            html.H2(
                                "Un bug ? Un nouveau graphique/une nouvelle fonctionnalité ?",
                                className="mt-4",
                            ),
                            html.P(
                                [
                                    "Vous avez rencontré un bug en utlisant le site ? Vous avez une idée de nouvelle fonctionnalité "
                                    "ou de nouveau graphique ? N'hésitez pas à en faire part en ouvrant une issue ",
                                    html.A(
                                        "ici",
                                        href="https://github.com/MickaelFontes/noplp-stats/issues",
                                        target="_blank",
                                    ),
                                    " !",
                                ]
                            ),
                            html.P(
                                [
                                    "Si vous remarquez une erreur sur ",
                                    html.Strong("les données"),
                                    ", n'hésitez pas à contribuer ",
                                    html.A(
                                        "au wiki",
                                        href="https://n-oubliez-pas-les-paroles.fandom.com/fr/wiki/Wiki_N%27oubliez_pas_les_paroles",
                                        target="_blank",
                                    ),
                                    " !",
                                ]
                            ),
                            html.H2("Remerciement", className="mt-4"),
                            html.P(
                                "Un grand merci à tous les contributeurs du Fandom NOPLP pour leur énorme travail sans quoi tout ceci ne pourrait exister !"
                            ),
                        ],
                        md=8,
                    ),
                ]
            ),
        ],
        style={"marginTop": 20},
    )


# Keep this for backwards compatibility if needed
layout = get_home_layout()
