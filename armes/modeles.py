"""modeles.py - Modèles 3D des armes en vue subjective, chacune avec sa propre direction
artistique :
  AR-15        militaire   : vert olive + sable, point rouge
  Kriss Vector futuriste   : noir mat + néons cyan, viseur holographique
  DRS-50       arctique    : blanc/bleu acier, énorme lunette
  Pompe        western     : noyer + laiton + cartouches rouges
  Pistolet     chrome luxe : chrome + or
Le Titan porte la MÊME arme en version géante (x2.6) avec plaques d'armure orange.
Chaque pièce : (taille, position, couleur)."""
from ursina import Entity, color, Color


def c(h, s, v):
    return color.hsv(h, s, v)


NOIR, GANT = c(0, 0, .08), c(0, 0, .06)
CYAN, ROUGE, ORANGE = Color(.2, .95, 1, 1), Color(1, .08, .08, 1), Color(1, .5, .08, 1)
OR, LAITON, CHROME, NOYER = c(45, .85, .85), c(45, .75, .6), c(0, 0, .85), c(25, .7, .3)
MAINS = [((.07, .07, .14), (0, -.03, .32), GANT), ((.07, .09, .1), (0, -.1, -.1), GANT)]

MODELES = {
    'AR-15': [((.085, .11, .44), (0, 0, .04), c(85, .38, .27)), ((.05, .025, .4), (0, .07, .05), NOIR),
              ((.07, .07, .3), (0, -.005, .4), c(38, .42, .52)), ((.03, .03, .25), (0, .01, .7), NOIR),
              ((.045, .045, .06), (0, .01, .84), c(0, 0, .04)), ((.075, .11, .26), (0, -.01, -.3), c(38, .42, .5)),
              ((.08, .12, .03), (0, -.01, -.44), NOIR), ((.05, .17, .09), (0, -.13, .06), c(38, .42, .45)),
              ((.05, .12, .06), (0, -.11, -.1), NOIR),
              ((.012, .06, .03), (-.03, .1, .1), NOIR), ((.012, .06, .03), (.03, .1, .1), NOIR),
              ((.07, .012, .03), (0, .135, .1), NOIR), ((.011, .011, .01), (0, .105, .125), ROUGE)],
    'Kriss Vector': [((.1, .1, .34), (0, 0, .04), c(0, 0, .09)), ((.07, .04, .3), (0, .07, .05), c(0, 0, .15)),
                     ((.102, .02, .2), (0, .02, .05), CYAN), ((.07, .07, .18), (0, 0, .3), c(0, 0, .12)),
                     ((.025, .025, .12), (0, 0, .43), c(0, 0, .04)), ((.045, .28, .07), (0, -.19, .08), c(0, 0, .09)),
                     ((.047, .2, .02), (0, -.19, .115), CYAN), ((.06, .05, .2), (0, .02, -.25), c(0, 0, .12)),
                     ((.045, .09, .05), (0, -.09, -.07), NOIR), ((.04, .08, .04), (0, -.07, .28), NOIR),
                     ((.012, .06, .04), (-.03, .1, .1), c(0, 0, .07)), ((.012, .06, .04), (.03, .1, .1), c(0, 0, .07)),
                     ((.07, .012, .04), (0, .135, .1), c(0, 0, .07)), ((.01, .01, .008), (0, .1, .125), CYAN)],
    'DRS-50': [((.085, .1, .5), (0, 0, .05), c(200, .05, .92)), ((.087, .03, .5), (0, -.02, .05), c(205, .35, .45)),
               ((.035, .035, .9), (0, .01, .8), c(210, .25, .22)), ((.06, .06, .12), (0, .01, 1.27), NOIR),
               ((.055, .055, .32), (0, .095, .08), c(0, 0, .1)), ((.075, .075, .07), (0, .095, .27), c(0, 0, .12)),
               ((.075, .075, .07), (0, .095, -.1), c(0, 0, .12)), ((.05, .05, .01), (0, .095, .31), Color(.3, .6, 1, 1)),
               ((.08, .13, .34), (0, -.02, -.38), c(200, .05, .88)), ((.07, .04, .2), (0, .06, -.35), c(205, .35, .45)),
               ((.05, .1, .07), (0, -.09, 0), NOIR), ((.05, .1, .06), (0, -.1, -.14), NOIR),
               ((.012, .13, .012), (-.035, -.09, .55), c(210, .25, .22)), ((.012, .13, .012), (.035, -.09, .55), c(210, .25, .22))],
    'Pompe': [((.075, .1, .3), (0, 0, 0), c(210, .15, .25)), ((.077, .05, .12), (0, 0, .02), LAITON),
              ((.045, .045, .75), (0, .025, .5), c(210, .15, .2)), ((.035, .035, .55), (0, -.03, .42), c(210, .1, .3)),
              ((.075, .065, .22), (0, -.03, .3), NOYER), ((.075, .13, .34), (0, -.02, -.32), NOYER),
              ((.078, .13, .03), (0, -.02, -.5), c(25, .7, .15)), ((.014, .03, .014), (0, .06, .85), OR),
              ((.03, .03, .07), (.052, 0, -.05), ROUGE), ((.03, .03, .07), (.052, 0, .04), ROUGE),
              ((.03, .03, .07), (.052, 0, .13), ROUGE)],
    'Pistolet': [((.05, .065, .27), (0, .01, .05), CHROME), ((.048, .04, .2), (0, -.03, .03), c(0, 0, .55)),
                 ((.045, .13, .07), (0, -.09, -.06), c(0, 0, .2)), ((.047, .1, .04), (0, -.09, -.06), OR),
                 ((.02, .02, .04), (0, .01, .2), OR), ((.014, .024, .014), (0, .05, -.07), NOIR),
                 ((.014, .024, .014), (0, .05, .17), NOIR)],
}
PLAQUE_TITAN = [((.14, .05, .5), (0, .1, .1), c(20, .9, .75)), ((.09, .014, .4), (0, .045, .05), ORANGE),
                ((.12, .12, .05), (0, 0, .62), c(20, .9, .55))]

MUZZLE = {'AR-15': (0, .01, .88), 'Kriss Vector': (0, 0, .5), 'DRS-50': (0, .01, 1.35), 'Pompe': (0, .02, .9),
          'Pistolet': (0, .01, .23)}
FLASH = {'AR-15': (Color(1, .8, .3, .95), .24), 'Kriss Vector': (Color(.4, .95, 1, .95), .2),
         'DRS-50': (Color(.85, .92, 1, .95), .45), 'Pompe': (Color(1, .5, .1, .95), .5),
         'Pistolet': (Color(1, .95, .8, .95), .16)}
# hauteur du viseur : la racine de l'arme se place à (0, -hauteur, z) pour aligner la mire
ADS = {'AR-15': (0, -.105, .8), 'Kriss Vector': (0, -.1, .62), 'DRS-50': (0, -.095, .85),
       'Pompe': (0, -.065, .85), 'Pistolet': (0, -.05, .42)}
ECHELLE_TITAN = 2.6

# fusil porté par les bots (taille, couleur) : même identité visuelle que la vue subjective
BOT = {'AR-15': ((.1, .12, .75), c(85, .38, .27)), 'Kriss Vector': ((.1, .12, .55), c(180, .8, .3)),
       'DRS-50': ((.09, .1, 1.1), c(200, .05, .9)), 'Pompe': ((.1, .12, .85), NOYER),
       'Pistolet': ((.06, .08, .3), CHROME)}


def ads(nom, titan=False):
    x, y, z = ADS.get(nom, ADS['Pistolet'])
    k = ECHELLE_TITAN if titan else 1
    return (x * k, y * k, z * k)


def construire(nom, parent, titan=False):
    """Crée le modèle sous `parent` (sans éclairage = lisible en toute lumière)."""
    racine = Entity(parent=parent, ignore=True)
    pieces = list(MODELES.get(nom, MODELES['Pistolet'])) + MAINS
    if titan:
        pieces += PLAQUE_TITAN
        racine.scale = ECHELLE_TITAN
    for sc, pos, col in pieces:
        Entity(parent=racine, model='cube', scale=sc, position=pos, color=col, ignore=True)
    col, taille = FLASH.get(nom, FLASH['AR-15'])
    racine.flash = Entity(parent=racine, model='sphere', scale=taille * (1.4 if titan else 1),
                          position=MUZZLE.get(nom, (0, 0, .5)), color=col, enabled=False, ignore=True)
    return racine
