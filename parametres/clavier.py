"""clavier.py - Touches ET boutons de souris attribuables.
Chaque action a jusqu'à 2 touches (clavier, souris, molette). Modifiables en jeu via
Echap > Options (sauvegardé dans parametres/config.json)."""
import copy
from ursina import held_keys

# (action, libellé affiché) dans l'ordre du menu
ACTIONS = [
    ('avant', 'Avancer'), ('arriere', 'Reculer'), ('gauche', 'Gauche'), ('droite', 'Droite'),
    ('saut', 'Saut / grimper'), ('sprint', 'Sprint'), ('glisse', 'Glisser'),
    ('tir', 'Tirer'), ('viser', 'Viser'), ('recharge', 'Recharger'),
    ('arme1', 'Arme 1'), ('arme2', 'Arme 2'), ('arme_suiv', 'Arme suivante'), ('arme_prec', 'Arme precedente'),
    ('tactique', 'Grenade / fumigene'), ('grappin', 'Grappin'),
    ('titan', 'Appeler le Titan'), ('interagir', 'Embarquer / ejecter'),
]

TOUCHES = {
    'avant': ('z', 'w'), 'arriere': ('s',), 'gauche': ('q', 'a'), 'droite': ('d',),
    'sprint': ('left shift',), 'saut': ('space',), 'glisse': ('left control', 'c'),
    'tir': ('left mouse',), 'viser': ('right mouse',), 'recharge': ('r',),
    'titan': ('f',), 'interagir': ('e',), 'tactique': ('g',), 'grappin': ('x',),
    'arme1': ('1',), 'arme2': ('2',), 'arme_suiv': ('scroll up',), 'arme_prec': ('scroll down',),
}
DEFAUT = copy.deepcopy(TOUCHES)

# actions "maintenues" : la molette n'a pas d'état maintenu
MAINTENUES = ('avant', 'arriere', 'gauche', 'droite', 'sprint', 'tir', 'viser')

NOMS = {'left mouse': 'Clic G', 'right mouse': 'Clic D', 'middle mouse': 'Clic molette',
        'scroll up': 'Molette +', 'scroll down': 'Molette -', 'left shift': 'Maj G', 'right shift': 'Maj D',
        'left control': 'Ctrl G', 'right control': 'Ctrl D', 'left alt': 'Alt G', 'space': 'Espace',
        'tab': 'Tab', 'enter': 'Entree', 'backspace': 'Retour', 'up arrow': 'Haut', 'down arrow': 'Bas',
        'left arrow': 'Gauche', 'right arrow': 'Droite'}


def nom(touche):
    return NOMS.get(touche, touche.upper())


def tenu(action):
    """True si une des touches de l'action est maintenue."""
    return any(held_keys[k] for k in TOUCHES[action])


def axe(plus, moins):
    return float(tenu(plus)) - float(tenu(moins))


def normaliser(key):
    """Transforme un évènement input() en nom de touche attribuable (ou None)."""
    if key.endswith(' up') or key.endswith(' hold') or key.startswith('gamepad') \
            or key in ('escape', 'mouse move', 'mouse wheel'):
        return None
    return key[:-5] if key.endswith(' down') else key


def est(key, action):
    k = normaliser(key)
    return k is not None and k in TOUCHES[action]


def assigner(action, slot, touche):
    """Attribue `touche` au slot (0/1) de l'action ; la retire des autres actions."""
    if touche in MAINTENUES_INTERDITES(action):
        return False
    for a, ks in TOUCHES.items():
        if a != action and touche in ks:
            TOUCHES[a] = tuple(k for k in ks if k != touche)
    ks = list(TOUCHES[action]) + [''] * 2
    ks = ks[:2]
    ks[slot] = touche
    TOUCHES[action] = tuple(k for k in ks if k)
    return True


def MAINTENUES_INTERDITES(action):
    """Pas de molette sur une action maintenue (elle n'a pas d'état 'enfoncé')."""
    return ('scroll up', 'scroll down') if action in MAINTENUES else ()


def effacer(action, slot):
    ks = list(TOUCHES[action])
    if slot < len(ks):
        ks.pop(slot)
    TOUCHES[action] = tuple(ks)


def slot_nom(action, slot):
    ks = TOUCHES[action]
    return nom(ks[slot]) if slot < len(ks) else '---'


def reinitialiser():
    for a, k in DEFAUT.items():
        TOUCHES[a] = k
