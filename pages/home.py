"""Home page layout."""

import dash
import dash_bootstrap_components as dbc
from dash import dcc

dash.register_page(__name__, path="/", title="NOLPL stats")

homepage_markdown = """
## Présentation

Le but de cet outil est de présenter diverses statistiques sur les chansons demandées sur l'émission *N'oubliez pas les paroles*.  
Elles peuvent être utilisées pour organiser ses révisions, ou simplement pour satisfaire sa curiosité.

**NB:** Cette remarque s'applique à tout ce qui va suivre. **Toutes** les données exploitées par ce site (paroles, apparitions des chansons, etc.) sont extraites du Fandom NOLPL.  
Elles peuvent être parfois incomplètes ou incorrectes. Ainsi, les statistiques affichées ici sont parfois inexactes puisque basées sur des données incomplètes.  
Malgré ces défauts, elles permettent quand-même d'extraire de précieuses informations.

## Fonctionnalités

### Les statistiques

Pour cela, divers onglets de visualisation sont à votre disposition:

* **Global**: statistiques sur l'ensemble des chansons et des catégories, sur la fenêtre temporelle sélectionnée.
* **Par catégorie**: statistiques spécifiques à chaque catégorie de l'émission (*Même chanson*, *50/40/... points*, *Maestro*)
* **Par chanson**: toutes les informations relatives à une chanson:
    * Nombre d'occurences par catégorie
    * Classements selon son nombre d'apparitions
    * Paroles
* **Par interprète**: pour un.e interprète donné.e, affiche les chansons apparues dans l'émission et les statistiques correspondantes.

### Entraînement

Cet onglet a pour but de vous aider à réviser une chanson !  
Pour cela, vous devez taper ses paroles **exactes** (comme dans l'émission) qui seront comparées à celles enregistrées sur le [Fandom NOPLP](https://n-oubliez-pas-les-paroles.fandom.com/fr/wiki/Wiki_N%27oubliez_pas_les_paroles).

L'objectif est de taper toutes les paroles et ainsi remplir la barre de progression jusqu'au bout !

## Un bug ? Un nouveau graphique/une nouvelle fonctionnalité ?

Vous avez rencontré un bug en utlisant le site ? Vous avez une idée de nouvelle fonctionnalité ou de nouveau graphique ?  
N'hésitez pas à en faire part en ouvrant une issue [**ici**](https://github.com/MickaelFontes/noplp-stats/issues) !

Si vous remarquez une erreur sur **les données**, n'hésitez pas à contribuer [au wiki](https://n-oubliez-pas-les-paroles.fandom.com/fr/wiki/Wiki_N%27oubliez_pas_les_paroles) ! 

## Remerciement 

Un grand merci à tous les contributeurs du Fandom NOPLP pour leur énorme travail sans quoi tout ceci ne pourrait exister !

"""  # noqa: W291,E501

layout = dbc.Container(
    children=[dcc.Markdown(homepage_markdown)],
    style={"marginTop": 20},
)
