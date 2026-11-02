"""sniper.py - DRS-50 (classe Sniper) : arctique blanc/bleu, lunette x5, traçantes blanches."""
from ursina import Color
from armes.arme import Arme


def creer():
    return Arme('DRS-50', degats=95, cadence=1.2, chargeur=5, reserve=20, portee=300,
                dispersion=.06, auto=False, recharge=2.4, zoom=20, ads_prec=.05,
                vue=((.08, .1, 1.0), (.3, -.28, .9)), recul=.2, pref=45,
                couleur_trace=Color(.85, .93, 1, 1), ep=.05)
