from .craft_commun import donnees, message

TOUCHE = 'v'
GAIN_ARMURE = 40
MAX_KITS = 3


def craft(p):
    d = donnees(p)
    d['bleu'] += 1
    if d['kits_armure'] >= MAX_KITS:
        message(p, "Kits d'armure au maximum.")
        return False
    d['kits_armure'] += 1
    message(p, f"Kit d'armure crafté ({d['kits_armure']}/{MAX_KITS}) - touche {TOUCHE.upper()}")
    return True


def utiliser(p):
    d = donnees(p)
    if d['kits_armure'] <= 0 or not p.vivant:
        return False
    mx = getattr(p, 'armure_max', 100)
    if getattr(p, 'armure', 0) >= mx:
        return False
    d['kits_armure'] -= 1
    p.armure = min(mx, getattr(p, 'armure', 0) + GAIN_ARMURE)
    return True