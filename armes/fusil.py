"""fusil.py - AR-15 (classe Assaut) : militaire, point rouge, traçantes jaunes."""
from ursina import Color
from armes.arme import Arme


def creer():
    return Arme('AR-15', degats=15, cadence=.09, chargeur=30, reserve=120, portee=130,
                dispersion=.014, auto=True, recharge=1.5, zoom=62, ads_prec=.35,
                vue=((.09, .11, .6), (.32, -.28, .7)), recul=.06, pref=22,
                couleur_trace=Color(1, .85, .3, 1))
