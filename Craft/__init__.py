from .craft_commun import donnees
from . import craft_amelioration, craft_classe, craft_augmentation
from . import craft_grenade, craft_armure, craft_soin


def on_loot(p, type_loot):
    """Retourne True/False si le loot est géré par le craft (pris ou refusé), None sinon
    (ex. 'munitions' : laisser le comportement normal du pilote)."""
    if type_loot == 'arme':                      # loot ROUGE
        d = donnees(p)
        d['rouge'] += 1
        n = d['rouge']
        craft_amelioration.verifier(p, n)        # 3
        craft_classe.verifier(p, n)              # 5
        craft_augmentation.verifier(p, n)        # 10
        return True
    if type_loot == 'grenade':                   # ORANGE
        return craft_grenade.craft(p)
    if type_loot == 'armure':                    # BLEU
        return craft_armure.craft(p)
    if type_loot == 'soin':                      # VERT
        return craft_soin.craft(p)
    return None


def touche(key, p):
    """À appeler dans l'input() du joueur : craft.touche(key, E.joueur)."""
    if key == craft_soin.TOUCHE:
        return craft_soin.utiliser(p)
    if key == craft_armure.TOUCHE:
        return craft_armure.utiliser(p)
    return False