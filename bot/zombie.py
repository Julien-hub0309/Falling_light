"""zombie.py - Zombies : lents et faibles le jour, rapides et forts la nuit."""
import math
import random
from ursina import *
import etat as E
import effets as FX
from bot import navigation as Nav
from bot.modeles import humanoide


class Zombie(Entity):
    volatile = True
    est_zombie = True

    def __init__(self, pos):
        super().__init__(position=Vec3(pos.x, 0, pos.z))
        self.r, self.h, self.vivant = .45, 1.9, True
        self.nuit = E.partie.nuit
        self.hp = self.hp_max = 70 if self.nuit else 40
        self.var = random.uniform(.85, 1.15)
        self.cible, self.pense, self.atk, self.flash = None, 0, 0, 0
        self.dest, self.dest_t, self.anim = None, 0, random.uniform(0, 6)
        self.route, self.rt, self.bloque, self.vy = [], 0, 0, 0
        self.m = humanoide(self, color.hsv(random.uniform(0, 360), .25, .3), color.hsv(220, .2, .2),
                           color.hsv(random.uniform(70, 110), .3, .45), pilote=False)
        self.corps = self.m['torse']
        self.recolorier()
        E.zombies.append(self)

    # ---- stats selon jour/nuit ----------------------------------------------
    @property
    def vitesse(self):
        return (4.6 if E.partie.nuit else 2.0) * self.var

    @property
    def degats(self):
        return 14 if E.partie.nuit else 7

    @property
    def detection(self):
        return 75 if E.partie.nuit else 32

    def recolorier(self):
        nuit = E.partie.nuit
        self.base = self.corps.color
        self.m['tete'].color = color.hsv(8, .5, .42) if nuit else color.hsv(85, .3, .5)
        for y in self.m['yeux']:
            y.color = Color(1, .1, .05, 1) if nuit else Color(.9, .8, .2, 1)

    def passer_nuit(self):
        """Appelé quand la nuit tombe : zombies plus forts (+75 % PV)."""
        self.hp *= 1.75
        self.hp_max *= 1.75
        self.recolorier()

    # ---- IA --------------------------------------------------------------------
    def trouver_cible(self):
        best, bd = None, self.detection
        for p in E.pilotes:
            if p.vivant and not p.elimine:
                d = math.hypot(p.x - self.x, p.z - self.z)
                if d < bd:
                    best, bd = p, d
        return best

    def avancer(self, dx, dz, dt):
        return E.marcher(self, dx, dz, self.vitesse, dt)

    def update(self):
        if not E.partie.actif:
            return
        dt = time.dt
        nuit = E.partie.nuit
        self.anim += dt * (9 if nuit else 5)
        ph = self.anim
        self.m['jambes'][0].rotation_x = math.sin(ph) * 35
        self.m['jambes'][1].rotation_x = -math.sin(ph) * 35
        lunge = 14 if self.atk > .5 else 0
        for i, bras in enumerate(self.m['bras']):
            bras.rotation_x = -80 + math.sin(ph * .7 + i * 2) * 8 + lunge
        self.m['tete'].rotation_z = 8 + math.sin(ph * .5) * 6
        self.flash -= dt
        self.corps.color = color.white if self.flash > 0 else self.base
        self.atk -= dt
        self.pense -= dt
        if self.pense <= 0:
            self.pense = random.uniform(.25, .45)
            self.cible = self.trouver_cible()
        c = self.cible
        if c is not None and (not c.vivant or c.elimine):
            c = self.cible = None
        if c is not None:
            haut = c.y - self.y > 2.5
            self.rt -= dt
            if (haut or self.bloque > .8) and self.rt <= 0:      # cible sur un toit / chemin bloqué : itinéraire
                self.rt, self.bloque = 2.5, 0
                self.route = Nav.route(self.position, c.position, c.y)
            but = self.route[0] if self.route else c.position
            d = Vec3(but.x - self.x, 0, but.z - self.z)
            dist = d.length()
            dc = math.hypot(c.x - self.x, c.z - self.z)
            if self.route and dist < 1.4:
                self.route.pop(0)
            elif dist > .01:
                dn = d * (1 / dist)
                self.rotation_y = math.degrees(math.atan2(dn.x, dn.z))
                if dc > 1.2 or self.route:
                    ok = self.avancer(dn.x, dn.z, dt)
                    self.bloque = 0 if ok else self.bloque + dt
            else:
                E.marcher(self, 0, 0, 0, dt)
            if dc < 1.7 and abs(c.y - self.y) < 2.2 and self.atk <= 0:
                self.atk = .7 if nuit else 1.0
                c.damage(self.degats, self)
        else:
            self.route = []
            self.dest_t -= dt
            if self.dest is None or self.dest_t <= 0:
                a = random.uniform(0, 6.28)
                self.dest, self.dest_t = Vec3(math.sin(a), 0, math.cos(a)), random.uniform(2, 5)
            if self.avancer(self.dest.x, self.dest.z, dt * .5):
                self.rotation_y = math.degrees(math.atan2(self.dest.x, self.dest.z))
            else:
                self.dest = None

    # ---- dégâts -------------------------------------------------------------------------
    def damage(self, n, source=None, tete=False):
        if not self.vivant:
            return
        self.hp -= n
        self.flash = .08
        FX.sang(self.position + Vec3(0, 1.3, 0), 3)
        if self.hp <= 0:
            self.vivant = False
            if self in E.zombies:
                E.zombies.remove(self)
            FX.sang(self.position + Vec3(0, 1.2, 0), 10)
            E.partie.mort_zombie(self, source)
            destroy(self)
