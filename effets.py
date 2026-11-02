"""effets.py - Particules et effets visuels : étincelles, sang, flash de bouche,
explosions (boule de feu, onde de choc, débris, fumée), secousse de caméra."""
import random
from ursina import *

shake = 0.0
_budget = 0
MAX = 160


def _libre(n):
    global _budget
    if _budget + n > MAX:
        return False
    _budget += n
    invoke(_rendre, n, delay=1.6)
    return True


def _rendre(n):
    global _budget
    _budget = max(0, _budget - n)


def _particule(pos, vec, col, taille, dur, gravite=True):
    e = Entity(model='cube', position=pos, scale=taille, color=col)
    cible = pos + vec
    if gravite:
        cible = Vec3(cible.x, cible.y - abs(vec.y) * .3 - .4, cible.z)
    e.animate_position(cible, duration=dur, curve=curve.out_quad)
    e.animate_scale(.001, duration=dur)
    destroy(e, delay=dur + .02)


def etincelles(pos, col=color.yellow, n=5, vit=2.2, dur=.35, taille=.07):
    if not _libre(n):
        return
    for _ in range(n):
        v = Vec3(random.uniform(-1, 1), random.uniform(.2, 1.2), random.uniform(-1, 1)) * vit
        _particule(pos, v, col, taille, dur * random.uniform(.7, 1.2))


def sang(pos, n=7):
    if not _libre(n):
        return
    for _ in range(n):
        v = Vec3(random.uniform(-1, 1), random.uniform(.3, 1.4), random.uniform(-1, 1)) * 2.2
        _particule(pos, v, color.hsv(0, .9, random.uniform(.35, .6)), random.uniform(.05, .1), .5)


def flash(pos, taille=.2):
    e = Entity(model='sphere', position=pos, scale=taille, color=Color(1, .85, .4, .9))
    destroy(e, delay=.05)


def impact(pos):
    etincelles(pos, color.light_gray, 3, 1.6, .25, .05)


def explosion(pos, taille=8, col=color.orange):
    if taille < 4:   # petit : flash + débris
        flash(pos, taille * .5)
        etincelles(pos, col, 6, 2.5, .4, .1)
        return
    if not _libre(14):
        return
    c = (col[0], col[1], col[2])
    boule = Entity(model='sphere', position=pos, scale=.3, color=Color(*c, .9))
    boule.animate_scale(Vec3(taille, taille, taille), duration=.28, curve=curve.out_expo)
    boule.animate_color(Color(.25, .1, .05, 0), duration=.55)
    destroy(boule, delay=.6)
    coeur = Entity(model='sphere', position=pos, scale=.2, color=Color(1, 1, .85, 1))
    coeur.animate_scale(Vec3(taille * .55, taille * .55, taille * .55), duration=.15)
    coeur.animate_color(Color(1, 1, .8, 0), duration=.2)
    destroy(coeur, delay=.25)
    onde = Entity(model='sphere', position=Vec3(pos.x, max(pos.y, .15), pos.z), scale=(.5, .12, .5),
                  color=Color(1, 1, 1, .3))
    onde.animate_scale(Vec3(taille * 2.3, .15, taille * 2.3), duration=.3, curve=curve.out_expo)
    onde.animate_color(Color(1, 1, 1, 0), duration=.3)
    destroy(onde, delay=.35)
    for _ in range(6):
        v = Vec3(random.uniform(-1, 1), random.uniform(.5, 1.6), random.uniform(-1, 1)) * taille * .45
        _particule(pos, v, color.hsv(random.uniform(10, 40), .9, 1), random.uniform(.12, .3), .7)
    for _ in range(3):
        f = Entity(model='sphere', position=pos + Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)) * taille * .2,
                   scale=taille * .3, color=Color(.22, .22, .22, .55))
        f.animate_position(f.position + Vec3(0, taille * .9, 0), duration=1.4)
        f.animate_scale(Vec3(taille * .8, taille * .8, taille * .8), duration=1.4)
        f.animate_color(Color(.2, .2, .2, 0), duration=1.4)
        destroy(f, delay=1.45)


def secousse(a):
    global shake
    shake = max(shake, min(a, 1.6))
