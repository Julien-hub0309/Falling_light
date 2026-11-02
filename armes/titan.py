"""titan.py - Arme du Titan = l'arme PRINCIPALE de son pilote en version surpuissante :
dégâts x3, chargeur x3, munitions infinies, portée x1.4, balles traçantes épaisses."""
import copy


def pour(arme):
    t = copy.copy(arme)
    t.titan = True
    t.nom = f'{arme.nom} TITAN'
    t.degats = arme.degats * 3
    t.cadence = arme.cadence * 1.15
    t.chargeur = t.munitions = arme.chargeur * 3
    t.reserve = None                       # infinies
    t.t_recharge = arme.t_recharge * .8
    t.portee = arme.portee * 1.4
    t.dispersion = arme.dispersion * .7
    t.recul = arme.recul * 2
    t.ep = arme.ep * 4
    t.pref = arme.pref * 1.4
    t.vue = ((.5, .45, 1.6), (.95, -.85, 1.5))
    t.cool = t.rech = 0.0
    return t
