from .craft_commun import donnees, message

TOUCHE = 'h'
GAIN_VIE = 40
MAX_KITS = 3


def craft(p):
    d = donnees(p)
    d['vert'] += 1
    if d['kits_soin'] >= MAX_KITS:
        message(p, "Kits de soin au maximum.")
        return False
    d['kits_soin'] += 1
    message(p, f"Kit de soin crafté ({d['kits_soin']}/{MAX_KITS}) - touche {TOUCHE.upper()}")
    return True


def utiliser(p):
    d = donnees(p)
    if d['kits_soin'] <= 0 or not p.vivant:
        return False
    mx = getattr(p, 'vie_max', 100)
    if p.vie >= mx:
        return False
    d['kits_soin'] -= 1
    p.vie = min(mx, p.vie + GAIN_VIE)
    return True