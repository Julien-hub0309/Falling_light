from .craft_commun import donnees, message

PALIER = 3
BONUS_MELEE = .25          # +25 % de dégâts au corps à corps


def verifier(p, n_rouge):
    d = donnees(p)
    if n_rouge == PALIER and d['niveau_melee'] == 0:
        d['niveau_melee'] = 1
        p.mult_melee = 1 + BONUS_MELEE * d['niveau_melee']
        message(p, f"Amélioration mêlée : +{int(BONUS_MELEE * 100)} % de dégâts !")
        return True
    return False


def degats_melee(p, base):
    """À utiliser dans l'attaque au corps à corps : degats = craft_amelioration.degats_melee(self, 20)."""
    return base * getattr(p, 'mult_melee', 1)