"""options.py - Menu Options (Echap) : attribution des touches clavier / souris / molette,
sensibilité, FOV, inversion Y, qualité graphique. Sauvegarde auto dans config.json.
Pendant le match, ouvrir ce menu met la partie en PAUSE."""
import time as T
from ursina import *
import etat as E
from parametres import clavier as K, souris as S, graphismes as G, config


class OptionsMenu(Entity):
    def __init__(self):
        super().__init__()                 # reste activé pour recevoir Echap
        self.ouvert, self.capture, self.t_capture = False, None, 0
        self.p = Entity(parent=camera.ui, enabled=False, z=-1)
        Entity(parent=self.p, model='quad', scale=(1.75, .98), color=Color(.02, .03, .06, 1), z=.1)
        Entity(parent=self.p, model='quad', scale=(1.75, .006), y=.40, color=color.orange, z=.05)
        Text(parent=self.p, text='OPTIONS', origin=(0, 0), y=.45, scale=2, color=color.orange)
        Text(parent=self.p, text='TOUCHES  (clic sur une case, puis touche / bouton souris / molette)',
             position=(-.84, .385), scale=.8, color=color.light_gray)
        self.boutons = {}
        n = len(K.ACTIONS)
        lignes = (n + 1) // 2
        for i, (action, lib) in enumerate(K.ACTIONS):
            col, row = divmod(i, lignes)
            x0, y = -.84 + col * .6, .32 - row * .068
            Text(parent=self.p, text=lib, position=(x0, y + .012), scale=.85)
            for slot in (0, 1):
                b = Button(parent=self.p, text='', position=(x0 + .33 + slot * .125, y), scale=(.115, .05),
                           color=color.dark_gray)
                b.text_size = .7
                b.on_click = (lambda a=action, s=slot: self.demarrer_capture(a, s))
                self.boutons[(action, slot)] = b
        # ---- réglages à droite
        Text(parent=self.p, text='SOURIS / ECRAN', position=(.40, .385), scale=.8, color=color.light_gray)
        self.vals = {}
        self.ligne('sens', 'Sensibilite', .32, lambda d: self.pas('sens', d))
        self.ligne('fov', 'Champ de vision', .245, lambda d: self.pas('fov', d))
        self.ligne('inv', 'Inverser Y', .17, lambda d: self.pas('inv', d))
        self.ligne('qual', 'Graphismes', .095, lambda d: self.pas('qual', d))
        Text(parent=self.p, text='(graphismes : appliques au prochain lancement)', position=(.40, .045),
             scale=.6, color=color.gray)
        self.bouton('Reinitialiser les touches', (.62, -.04), self.reinit)
        self.bouton('Fermer  (Echap)', (.62, -.13), self.fermer)
        self.bouton('Quitter le jeu', (.62, -.22), application.quit, color.hsv(0, .6, .5))
        self.info = Text(parent=self.p, origin=(0, 0), y=-.43, scale=.8, color=color.light_gray,
                         text='Retour = effacer la case   |   Echap = annuler   |   Une touche deja utilisee est retiree de l\'autre action')
        self.maj()

    # ---- widgets
    def bouton(self, texte, pos, fn, col=color.dark_gray):
        b = Button(parent=self.p, text=texte, position=pos, scale=(.4, .065), color=col)
        b.text_size = .8
        b.on_click = fn
        return b

    def ligne(self, cle, lib, y, fn):
        Text(parent=self.p, text=lib, position=(.40, y + .012), scale=.85)
        for dx, sym, d in ((.58, '-', -1), (.80, '+', 1)):
            b = Button(parent=self.p, text=sym, position=(dx, y), scale=(.04, .045), color=color.dark_gray)
            b.on_click = (lambda d=d: fn(d))
        self.vals[cle] = Text(parent=self.p, text='', origin=(0, 0), position=(.69, y), scale=.9, color=color.yellow)

    # ---- valeurs
    def pas(self, cle, d):
        if cle == 'sens':
            S.SENSIBILITE = max(10, min(120, S.SENSIBILITE + 5 * d))
        elif cle == 'fov':
            S.FOV = max(70, min(120, S.FOV + 5 * d))
        elif cle == 'inv':
            S.INVERSER_Y = not S.INVERSER_Y
        elif cle == 'qual':
            i = (G.NIVEAUX.index(G.QUALITE) + d) % len(G.NIVEAUX)
            G.QUALITE = G.NIVEAUX[i]
        self.maj()

    def maj(self):
        self.vals['sens'].text = f'{int(S.SENSIBILITE)}'
        self.vals['fov'].text = f'{int(S.FOV)}'
        self.vals['inv'].text = 'Oui' if S.INVERSER_Y else 'Non'
        self.vals['qual'].text = G.QUALITE.upper()
        for (a, s), b in self.boutons.items():
            if self.capture == (a, s):
                b.text, b.color = '...', color.orange
            else:
                b.text, b.color = K.slot_nom(a, s), color.dark_gray
            b.text_size = .7

    def reinit(self):
        K.reinitialiser()
        self.annuler()

    # ---- capture d'une touche
    def demarrer_capture(self, action, slot):
        self.capture, self.t_capture = (action, slot), T.time()
        self.maj()

    def annuler(self):
        self.capture = None
        self.maj()

    def input(self, key):
        if self.capture is not None:
            if key == 'left mouse down' and T.time() - self.t_capture < .25:
                return                                  # le clic qui a ouvert la capture
            action, slot = self.capture
            if key == 'escape':
                self.annuler()
            elif key == 'backspace':
                K.effacer(action, slot)
                self.annuler()
            else:
                t = K.normaliser(key)
                if t is not None and K.assigner(action, slot, t):
                    self.annuler()
            return
        if key == 'escape':
            self.fermer() if self.ouvert else self.ouvrir()

    # ---- ouverture / fermeture
    def ouvrir(self):
        self.ouvert = True
        self.p.enabled = True
        self.maj()
        P = E.partie
        if P is not None and P.actif:
            P.pause = True
        mouse.locked = False
        mouse.visible = True

    def fermer(self):
        self.ouvert, self.capture = False, None
        self.p.enabled = False
        config.sauver()
        P = E.partie
        if P is not None and P.en_cours and not P.fini:
            P.pause = False
            mouse.locked = True
