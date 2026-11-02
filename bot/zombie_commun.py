import math
import random
from ursina import *
import etat as E
import effets as FX
from bot import navigation as Nav
from bot.modeles import humanoide

RAYON_BRUIT_TIR = 90          # portée par défaut du bruit d'un coup de feu


# ---------------------------------------------------------------- groupes ---
def tailles_groupes(total, tmin, tmax):
    """Découpe `total` zombies en groupes de tmin à tmax, somme exacte (ex. 40 -> 3,4,4,3...)."""
    k = random.randint(-(-total // tmax), total // tmin)        # nombre de groupes possible
    tailles = [tmin] * k
    reste = total - tmin * k
    while reste > 0:
        i = random.randrange(k)
        if tailles[i] < tmax:
            tailles[i] += 1
            reste -= 1
    return tailles


def _pos_defaut():
    return Vec3(random.uniform(-90, 90), 0, random.uniform(-90, 90))


def generer_groupes(classe, total, tmin, tmax, pos_fn=None):
    """Crée `total` zombies de `classe`, répartis en groupes de tmin..tmax.
    pos_fn() doit renvoyer un point de spawn valide (Vec3) ; un groupe apparaît autour de ce point."""
    pos_fn = pos_fn or _pos_defaut
    crees = []
    for n in tailles_groupes(total, tmin, tmax):
        centre = pos_fn()
        groupe = []
        for _ in range(n):
            z = classe(Vec3(centre.x + random.uniform(-3, 3), 0, centre.z + random.uniform(-3, 3)))
            z.groupe = groupe
            groupe.append(z)
        crees += groupe
    return crees


# ------------------------------------------------------------------ bruit ---
def bruit(pos, rayon=RAYON_BRUIT_TIR):
    """À appeler à chaque coup de feu : alerte les zombies qui écoutent (spéciaux le jour, rapaces la nuit).
    Arme silencieuse -> passer un `rayon` plus petit."""
    for z in list(E.zombies):
        if z.vivant and z.ECOUTE_BRUIT and math.hypot(z.x - pos.x, z.z - pos.z) < rayon:
            z.alerter(pos)


# ------------------------------------------------------------ zombie de base ---
class ZombieBase(Entity):
    volatile = True
    est_zombie = True

    # --- stats : redéfinies dans les sous-classes ---
    type_zombie = 'normal'
    HP, MULT_HP = 40, 1
    VITESSE, MULT_VITESSE = 2.0, 1
    DEGATS = 7
    DETECTION = 32
    DELAI_ATTAQUE = 1.0
    ANIM_VITESSE = 5
    ECOUTE_BRUIT = False                       # True : attiré par les coups de feu
    COULEUR_TETE = color.hsv(85, .3, .5)
    COULEUR_YEUX = Color(.9, .8, .2, 1)

    def __init__(self, pos):
        super().__init__(position=Vec3(pos.x, 0, pos.z))
        self.r, self.h, self.vivant = .45, 1.9, True
        self.hp = self.hp_max = self.HP * self.MULT_HP
        self.var = random.uniform(.85, 1.15)
        self.cible, self.pense, self.atk, self.flash = None, 0, 0, 0
        self.dest, self.dest_t, self.anim = None, 0, random.uniform(0, 6)
        self.route, self.rt, self.bloque, self.vy = [], 0, 0, 0
        self.groupe = [self]
        self.alerte_pos, self.alerte_t = None, 0
        self.m = humanoide(self, color.hsv(random.uniform(0, 360), .25, .3), color.hsv(220, .2, .2),
                           color.hsv(random.uniform(70, 110), .3, .45), pilote=False)
        self.corps = self.m['torse']
        self.base = self.corps.color
        self.m['tete'].color = self.COULEUR_TETE
        for y in self.m['yeux']:
            y.color = self.COULEUR_YEUX
        E.zombies.append(self)

    @property
    def vitesse(self):
        return self.VITESSE * self.MULT_VITESSE * self.var

    # ---- bruit / groupe -----------------------------------------------------
    def alerter(self, pos, propage=True):
        """Va enquêter sur un bruit (et prévient son groupe)."""
        self.alerte_pos, self.alerte_t = Vec3(pos.x, pos.y, pos.z), 12
        if propage:
            for g in self.groupe:
                if g is not self and g.vivant:
                    g.alerter(pos, False)

    # ---- IA ----------------------------------------------------------------
    def trouver_cible(self):
        best, bd = None, self.DETECTION
        for p in E.pilotes:
            if p.vivant and not p.elimine:
                d = math.hypot(p.x - self.x, p.z - self.z)
                if d < bd:
                    best, bd = p, d
        if best is None:                                   # le groupe partage sa cible
            for g in self.groupe:
                if g is not self and g.vivant and g.cible is not None and g.cible.vivant:
                    return g.cible
        return best

    def avancer(self, dx, dz, dt):
        return E.marcher(self, dx, dz, self.vitesse, dt)

    def enquete(self, dt):
        """Marche vers l'endroit du dernier bruit, puis se calme."""
        p = self.alerte_pos
        self.alerte_t -= dt
        if self.alerte_t <= 0 or math.hypot(p.x - self.x, p.z - self.z) < 2.5:
            self.alerte_pos, self.alerte_t, self.route = None, 0, []
            return
        self.rt -= dt
        if self.bloque > .8 and self.rt <= 0:
            self.rt, self.bloque = 2.5, 0
            self.route = Nav.route(self.position, p, p.y)
        but = self.route[0] if self.route else p
        d = Vec3(but.x - self.x, 0, but.z - self.z)
        dist = d.length()
        if self.route and dist < 1.4:
            self.route.pop(0)
        elif dist > .01:
            dn = d * (1 / dist)
            self.rotation_y = math.degrees(math.atan2(dn.x, dn.z))
            ok = self.avancer(dn.x, dn.z, dt)
            self.bloque = 0 if ok else self.bloque + dt

    def update(self):
        if not E.partie.actif:
            return
        dt = time.dt
        self.anim += dt * self.ANIM_VITESSE
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
            self.alerte_pos, self.alerte_t = None, 0
            haut = c.y - self.y > 2.5
            self.rt -= dt
            if (haut or self.bloque > .8) and self.rt <= 0:      # cible sur un toit / chemin bloqué
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
                self.atk = self.DELAI_ATTAQUE
                c.damage(self.DEGATS, self)
        elif self.alerte_pos is not None:
            self.enquete(dt)
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

    # ---- dégâts ------------------------------------------------------------
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
            if self in self.groupe:
                self.groupe.remove(self)
            FX.sang(self.position + Vec3(0, 1.2, 0), 10)
            E.partie.mort_zombie(self, source)
            destroy(self)