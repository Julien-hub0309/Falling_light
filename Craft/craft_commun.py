import etat as E

DEFAUT = {'rouge': 0, 'orange': 0, 'bleu': 0, 'vert': 0,
          'kits_soin': 0, 'kits_armure': 0, 'grenades': {},
          'niveau_melee': 0, 'arme_classe': False, 'augmentation': False}


def donnees(p):
    """Dictionnaire de craft du pilote (créé à la première utilisation)."""
    if not hasattr(p, 'craft'):
        p.craft = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAUT.items()}
    return p.craft


def message(p, texte):
    """Affiche un message seulement pour le joueur (adapter à ton HUD si besoin)."""
    if p is getattr(E, 'joueur', None):
        print(texte)


def donner_arme(p, nom):
    if hasattr(p, 'donner_arme'):
        p.donner_arme(nom)
    else:
        p.armes = getattr(p, 'armes', [])
        if nom not in p.armes:
            p.armes.append(nom)