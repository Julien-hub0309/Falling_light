from ursina import Color
from armes.arme import Arme


def creer():
    return Arme('Couteau', degats=3, cadence=1, chargeur=0, reserve=100,
                portee=10, dispersion=.05, auto=False, recharge=0,
                zoom=4, ads_prec=.2, vue=((.5, .5, 1), (.8, -.8, 1)),
                recul=0, pref=5, couleur_trace=Color(1, .25, .25, 1))