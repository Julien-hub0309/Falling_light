"""loot.py - Objets à ramasser : soin, munitions, armure, grenade, arme."""
import math
import random
from ursina import *
import etat as E

TYPES = {'soin': (color.lime, 5), 'munitions': (color.yellow, 5), 'armure': (color.azure, 3),
         'grenade': (color.orange, 2), 'arme': (color.red, 3)}


class Loot(Entity):
    def __init__(self, pos, type=None, temporaire=False):
        super().__init__(position=Vec3(pos.x, pos.y, pos.z))
        self.type = type or random.choices(list(TYPES), weights=[v[1] for v in TYPES.values()])[0]
        col = TYPES[self.type][0]
        self.cube = Entity(parent=self, model='cube', color=col, scale=.5, y=.7, ignore=True)
        Entity(parent=self, model='cube', color=Color(col[0], col[1], col[2], .35),
               scale=(.1, 7, .1), y=3.5, ignore=True)          # rayon lumineux repérable de loin
        self.temporaire, self.vie, self.actif = temporaire, 45, True
        self.t = random.uniform(0, 6)
        E.loots.append(self)

    def update(self):
        """Animation (rotation / lévitation) seulement près du joueur."""
        j = E.joueur
        if not E.partie.actif or j is None or abs(j.x - self.x) > 70 or abs(j.z - self.z) > 70:
            return
        dt = time.dt
        self.t += dt
        self.cube.rotation_y += 90 * dt
        self.cube.y = .7 + math.sin(self.t * 2) * .12

    def prendre(self):
        if self.temporaire:
            self.retirer()
        else:
            self.actif, self.enabled = False, False
            E.partie.plus_tard(45, self.reapparaitre)

    def reapparaitre(self):
        self.actif, self.enabled = True, True

    def retirer(self):
        if self in E.loots:
            E.loots.remove(self)
        destroy(self)


def reset_loots():
    for l in list(E.loots):
        if l.temporaire:
            l.retirer()
        else:
            l.reapparaitre()


def ramassage(dt):
    """Appelé ~10 fois/s par la partie : ramassage par les pilotes + durée de vie des loots temporaires."""
    for l in list(E.loots):
        if not l.actif:
            continue
        if l.temporaire:
            l.vie -= dt
            if l.vie <= 0:
                l.retirer()
                continue
        for p in E.pilotes:
            if p.vivant and not p.elimine and abs(p.x - l.x) < 1.6 and abs(p.z - l.z) < 1.6 \
                    and -1 < p.y - l.y < 2.4:
                if p.ramasser(l):
                    l.prendre()
                    break
