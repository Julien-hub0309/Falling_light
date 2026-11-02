import random
from ursina import *

import etat as E

from classe.classe_1 import CLASSE as ASSAUT
from classe.classe_2 import CLASSE as TACTIC
from classe.classe_3 import CLASSE as SNIPER
from classe.classe_4 import CLASSE as BRECHE

from armes.couteau import creer as creer_couteau

CLASSES = [ASSAUT, TACTIC, SNIPER, BRECHE]


def aleatoire():
    return random.choice(CLASSES)


def appliquer(p, c):
    """
    Applique une classe.
    Le joueur démarre avec un couteau uniquement.
    """

    p.classe = c

    # Vie
    p.hp_max = c["hp"]
    p.hp = c["hp"]

    # Armure
    p.armure = 0

    # Compétences
    p.tactique = c["tactique"]
    p.nb_tactique = c["nb_tactique"]
    p.vitesse_mult = c["vitesse"]

    # Arme de départ
    couteau = creer_couteau()

    # Deux slots pour éviter de casser
    # le système de changement d'arme
    p.armes = [couteau, couteau]

    p.idx = 0

    if hasattr(p, "sur_changement_arme"):
        p.sur_changement_arme()


class MenuClasse(Entity):

    def __init__(self, on_choix):
        super().__init__(parent=camera.ui)

        self.on_choix = on_choix

        Text(
            parent=self,
            text="FALLING LIGHT",
            origin=(0, 0),
            y=.40,
            scale=3.2,
            color=color.orange
        )

        Text(
            parent=self,
            text="Choisis ta classe (clic ou touches 1-4)",
            origin=(0, 0),
            y=.30,
            scale=1.4
        )

        for i, c in enumerate(CLASSES):
            x = -.66 + i * .44

            b = Button(
                parent=self,
                text=f"{i+1}\n{c['nom']}",
                position=(x, .1),
                scale=(.4, .25),
                color=color.dark_gray
            )

            b.on_click = lambda c=c: self.choisir(c)

            Text(
                parent=self,
                text=c["description"],
                position=(x - .18, -.08),
                scale=.9
            )

        Text(
            parent=self,
            text="Départ avec couteau uniquement",
            origin=(0, 0),
            y=-.25,
            scale=1,
            color=color.yellow
        )

        ob = Button(
            parent=self,
            text="OPTIONS / TOUCHES",
            position=(0, -.2),
            scale=(.35, .06),
            color=color.dark_gray
        )

        ob.on_click = lambda: E.options.ouvrir()

    def choisir(self, c):
        self.on_choix(c)

    def input(self, key):
        if E.options is not None and E.options.ouvert:
            return

        if key in ("1", "2", "3", "4"):
            self.choisir(CLASSES[int(key) - 1])