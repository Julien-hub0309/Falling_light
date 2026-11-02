"""modeles.py (bot) - Personnages articulés : pilotes (casque, gilet, sac, visière) et
zombies (bras tendus, yeux brillants). Retourne un dict de pièces pour l'animation."""
from ursina import *
import parametres.graphismes as G


def _c(parent, sc, pos, col, **kw):
    return G.solide(parent=parent, model='cube', scale=sc, position=pos, color=col, **kw)


def humanoide(racine, veste, pantalon, peau, botte=None, pilote=True):
    m = {'jambes': [], 'bras': []}
    botte = botte or color.hsv(0, 0, .1)
    for sx in (-1, 1):
        piv = Entity(parent=racine, position=(sx * .18, .88, 0), ignore=True)
        _c(piv, (.26, .88, .3), (0, -.44, 0), pantalon)
        _c(piv, (.28, .14, .42), (0, -.84, .06), botte)
        m['jambes'].append(piv)
    m['torse'] = _c(racine, (.74, .72, .4), (0, 1.26, 0), veste)
    _c(racine, (.7, .12, .38), (0, .93, 0), color.hsv(30, .3, .2))                # ceinture
    for sx in (-1, 1):
        piv = Entity(parent=racine, position=(sx * .47, 1.55, 0), ignore=True)
        _c(piv, (.2, .72, .22), (0, -.34, 0), veste)
        _c(piv, (.16, .16, .18), (0, -.74, 0), peau if not pilote else color.hsv(0, 0, .08))
        m['bras'].append(piv)
    m['tete'] = _c(racine, (.34, .36, .34), (0, 1.84, 0), peau)
    if pilote:
        _c(racine, (.4, .2, .4), (0, 1.99, -.01), veste)                           # casque
        Entity(parent=racine, model='cube', scale=(.3, .09, .05), position=(0, 1.85, .18),
               color=Color(.3, .9, 1, 1), ignore=True)                                 # visière lumineuse
        _c(racine, (.5, .55, .22), (0, 1.3, -.3), color.hsv(0, 0, .13))            # sac à dos
        m['fusil'] = _c(racine, (.1, .12, .75), (.3, 1.05, .45), color.hsv(0, 0, .1))   # fusil
        m['bras'][1].rotation_x = -75
    else:
        for b in m['bras']:
            b.rotation_x = -80
        m['yeux'] = [Entity(parent=racine, model='cube', scale=(.07, .05, .04), position=(sx * .08, 1.88, .18),
                            color=Color(1, .8, .1, 1), ignore=True) for sx in (-1, 1)]
        m['tete'].rotation_z = 8
    return m
