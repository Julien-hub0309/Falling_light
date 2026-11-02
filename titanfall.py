# FALLING LIGHT - FPS Titanfall x Dying Light (Python + Ursina)
# Installation :  pip install ursina pillow numpy
# Lancement    :  python titanfall.py
from ursina import *
from parametres import config, graphismes as G
config.charger()                      # touches / souris / graphismes sauvegardés

import etat as E
from map.map import construire_map
from bot.joueur import Player
from bot.ennemie import PiloteIA
from HUD.hud import HUD
from partie import Partie
from classe.choix_classe import MenuClasse
from parametres.options import OptionsMenu

app = Ursina(title='FALLING LIGHT')
window.exit_button.visible = False
E.ciel = Sky()
G.init()                              # éclairage, brouillard, soleil/lune
mouse.locked = False

construire_map()                      # immeubles, routes, décor, spawns, loot
E.joueur = Player()                   # pilote 1 : toi
for nom, col in (('Alpha', color.red), ('Bravo', color.orange),
                 ('Charlie', color.violet), ('Delta', color.green)):
    PiloteIA(nom, col)                # pilotes 2 à 5 : bots rivaux
E.hud = HUD()
E.partie = Partie(E.ciel)
E.menu = MenuClasse(E.partie.demarrer)
E.options = OptionsMenu()             # Echap : touches, souris, graphismes
E.partie.ouvrir_menu()

app.run()
