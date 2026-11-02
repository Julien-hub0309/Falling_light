from .craft_commun import donnees, message

PALIER = 10
AUGMENTATION = {'degats': 1.35, 'cadence': 1.2, 'chargeur': 1.5}   # multiplicateurs


def verifier(p, n_rouge):
    d = donnees(p)
    if n_rouge == PALIER and not d['augmentation']:
        if not d['arme_classe']:                 # sécurité : l'arme de classe doit exister
            return False
        d['augmentation'] = True
        p.aug_arme = dict(AUGMENTATION)
        message(p, "Arme à feu améliorée !")
        return True
    return False


def mult(p, cle):
    """Ex. : degats *= craft_augmentation.mult(self, 'degats') au moment du tir."""
    return getattr(p, 'aug_arme', {}).get(cle, 1)