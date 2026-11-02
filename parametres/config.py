"""config.py - Sauvegarde / chargement des réglages (touches, souris, graphismes)
dans parametres/config.json."""
import json
import os
from parametres import clavier, souris, graphismes

FICHIER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


def sauver():
    data = {'touches': {a: list(k) for a, k in clavier.TOUCHES.items()},
            'souris': {'sensibilite': souris.SENSIBILITE, 'inverser_y': souris.INVERSER_Y, 'fov': souris.FOV},
            'graphismes': {'qualite': graphismes.QUALITE}}
    try:
        with open(FICHIER, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        print('Config non sauvegardee :', e)


def charger():
    try:
        with open(FICHIER, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        return
    for a, k in data.get('touches', {}).items():
        if a in clavier.TOUCHES and isinstance(k, list):
            clavier.TOUCHES[a] = tuple(str(x) for x in k)
    s = data.get('souris', {})
    souris.SENSIBILITE = float(s.get('sensibilite', souris.SENSIBILITE))
    souris.INVERSER_Y = bool(s.get('inverser_y', souris.INVERSER_Y))
    souris.FOV = float(s.get('fov', souris.FOV))
    q = data.get('graphismes', {}).get('qualite')
    if q in graphismes.NIVEAUX:
        graphismes.QUALITE = q
