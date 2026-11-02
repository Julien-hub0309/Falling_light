import etat as E
from bot.zombie_commun import ZombieBase, bruit, generer_groupes
from bot.zombie_jour import ZombieJour, ZombieSpecialJour, lancer_partie_jour
from bot.zombie_nuit import ZombieNuit, Rapace, lancer_partie_nuit


class _Type(type):
    def __instancecheck__(cls, obj):           # isinstance(z, Zombie) reste vrai pour tous les zombies
        return isinstance(obj, ZombieBase)


class Zombie(metaclass=_Type):
    def __new__(cls, pos):
        return (ZombieNuit if E.partie.nuit else ZombieJour)(pos)


# l'ancien code appelait z.passer_nuit() à la tombée de la nuit : plus de transition (parties séparées)
if not hasattr(ZombieBase, "passer_nuit"):
    ZombieBase.passer_nuit = lambda self: None