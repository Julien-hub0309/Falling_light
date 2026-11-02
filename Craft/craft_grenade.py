from .craft_commun import donnees, message

# classe -> type de grenade ; les classes absentes utilisent la grenade "munition"
GRENADE_CLASSE = {'soldat': 'frag', 'sniper': 'fumigene', 'tank': 'explosive', 'medic': 'soin'}
COUT_MUNITIONS = 10        # coût de la grenade "munition" (si le pilote a des munitions)
MAX_GRENADES = 6


def type_grenade(p):
    return GRENADE_CLASSE.get(getattr(p, 'classe', None), 'munition')


def craft(p):
    d = donnees(p)
    d['orange'] += 1
    t = type_grenade(p)
    if t == 'munition':
        if hasattr(p, 'munitions'):
            if p.munitions < COUT_MUNITIONS:
                message(p, "Pas assez de munitions pour crafter une grenade.")
                return False
            p.munitions -= COUT_MUNITIONS
    if sum(d['grenades'].values()) >= MAX_GRENADES:
        message(p, "Stock de grenades plein.")
        return False
    d['grenades'][t] = d['grenades'].get(t, 0) + 1
    message(p, f"Grenade {t} craftée ({sum(d['grenades'].values())}/{MAX_GRENADES})")
    return True


def utiliser(p):
    """Retourne le type de grenade à lancer (ou None s'il n'y en a plus)."""
    d = donnees(p)
    t = type_grenade(p)
    if d['grenades'].get(t, 0) <= 0:
        t = next((k for k, v in d['grenades'].items() if v > 0), None)
    if t is None:
        return None
    d['grenades'][t] -= 1
    return t