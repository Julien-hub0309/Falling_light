"""hud.py - Interface : réticule, barres PV/armure, munitions, chrono jour/nuit, scores,
messages, minimap (bâtiments, pilotes proches, zombies proches, Titan)."""
import math
from ursina import *
import etat as E
import parametres.graphismes as G

MM_TAILLE, MM_POS = .36, Vec2(-.70, -.14)


def _barre(x, y, w, h, col):
    fond = Entity(parent=camera.ui, model='quad', origin=(-.5, 0), position=(x, y), scale=(w, h),
                  color=Color(0, 0, 0, .55))
    rempl = Entity(parent=camera.ui, model='quad', origin=(-.5, 0), position=(x, y), scale=(w, h * .7),
                   color=col, z=-.01)
    return fond, rempl


class HUD(Entity):
    def __init__(self):
        super().__init__()
        self.nuit = Entity(parent=camera.ui, model='quad', scale=(4, 2), z=2, color=Color(0, 0, .06, 0))
        self.hurt = Entity(parent=camera.ui, model='quad', scale=(4, 2), z=2, color=Color(1, 0, 0, 0))
        # réticule en croix
        self.cross = Entity(parent=camera.ui)
        self.cross_parts = [Entity(parent=self.cross, model='quad', scale=sc, position=pos, color=color.white)
                            for sc, pos in (((.012, .0025), (-.012, 0)), ((.012, .0025), (.012, 0)),
                                            ((.0025, .012), (0, .012)), ((.0025, .012), (0, -.012)))]
        Entity(parent=self.cross, model='quad', scale=.003, color=color.white)
        # lunette de sniper : fenêtre ronde simulée par 4 masques + réticule fin
        self.scope = [Entity(parent=camera.ui, model='quad', color=color.black, z=1, enabled=False, scale=sc, position=pos)
                      for sc, pos in (((4, 1), (0, .85)), ((4, 1), (0, -.85)), ((2, 2), (-1.35, 0)), ((2, 2), (1.35, 0)))]
        self.scope += [Entity(parent=camera.ui, model='quad', color=color.black, z=.8, enabled=False, scale=(.9, .002)),
                       Entity(parent=camera.ui, model='quad', color=color.black, z=.8, enabled=False, scale=(.002, .9))]
        # textes
        self.t_timer = Text('', origin=(0, 0), position=(0, .46), scale=2)
        self.t_phase = Text('', origin=(0, 0), position=(0, .41), scale=1.1)
        self.t_score = Text('', position=(-.88, .47), scale=1.1)
        self.t_feed = Text('', origin=(.5, .5), position=(.88, .47), scale=1.0, color=color.yellow)
        self.t_titan = Text('', origin=(0, 0), position=(0, .35), scale=1.2, color=color.orange)
        self.t_hp = Text('', position=(-.86, -.405), scale=1.0, color=color.white)
        self.t_ammo = Text('', origin=(.5, .5), position=(.88, -.40), scale=2.2)
        self.t_arme = Text('', origin=(.5, .5), position=(.88, -.455), scale=1.0, color=color.light_gray)
        self.t_info = Text('', origin=(.5, .5), position=(.88, -.345), scale=1.0, color=color.light_gray)
        self.banner = Text('', origin=(0, 0), y=.27, scale=2.6, color=color.orange)
        self.t_etat = Text('', origin=(0, 0), y=.12, scale=2, color=color.white)
        # barres
        _, self.b_hp = _barre(-.86, -.44, .32, .026, color.lime)
        _, self.b_arm = _barre(-.86, -.468, .32, .012, color.azure)
        # minimap
        self.mm = Entity(parent=camera.ui, model='quad', position=MM_POS, scale=MM_TAILLE,
                         color=Color(0, 0, 0, .55))
        k = MM_TAILLE / (2 * E.DEMI_MAP)
        for (x0, x1, z0, z1, y0, y1) in E.boxes:
            if (x1 - x0) > 14 and (z1 - z0) > 14 and y1 > 5 and x1 - x0 < 60 and y0 == 0:
                Entity(parent=camera.ui, model='quad', color=Color(.6, .65, .7, .6),
                       position=(MM_POS.x + (x0 + x1) / 2 * k, MM_POS.y + (z0 + z1) / 2 * k, -.01),
                       scale=((x1 - x0) * k, (z1 - z0) * k))
        self.pts_pil = [Entity(parent=camera.ui, model='quad', scale=.011, z=-.03, enabled=False) for _ in range(6)]
        self.pts_zom = [Entity(parent=camera.ui, model='quad', scale=.006, z=-.02, color=color.lime, enabled=False)
                        for _ in range(E.NB_ZOMBIES + 4)]
        self.pt_titan = Entity(parent=camera.ui, model='quad', scale=.012, z=-.03, color=color.orange, enabled=False)
        self.pt_moi = Entity(parent=camera.ui, model='quad', scale=(.011, .02), z=-.04, color=color.white)
        Text('ZQSD bouger | Espace saut/grimper | Echap options (touches, souris, graphismes)',
             origin=(0, 0), y=-.485, scale=.7, color=color.gray)
        self.hurt_a, self.hitm, self.ban_t, self.acc = 0, 0, 0, 0
        self.feed = []

    # ---- évènements ------------------------------------------------------------
    def degats(self):
        self.hurt_a = .45

    def touche(self, tete=False):
        self.hitm = .12 if not tete else .25

    def msg(self, texte, ttl=5):
        self.feed = (self.feed + [[texte, ttl]])[-6:]

    def banniere(self, texte, duree=3):
        self.banner.text, self.ban_t = texte, duree

    # ---- boucle --------------------------------------------------------------------
    def update(self):
        dt = time.dt
        j = E.joueur
        bas = j is not None and j.vivant and j.hp < j.hp_max * .3 and j.mode == 'pilot'
        pulse = .18 + .12 * abs(math.sin(time.time() * 5)) if bas else 0
        self.hurt_a = max(0, self.hurt_a - dt * .8)
        self.hurt.color = Color(1, 0, 0, max(self.hurt_a, pulse))
        self.hitm -= dt
        for p in self.cross_parts:
            p.color = color.red if self.hitm > 0 else color.white
        visee = j is not None and j.zoom
        lunette = visee and getattr(j, 'lunette', False)
        self.cross.enabled = not visee
        for e in self.scope:
            e.enabled = lunette
        if self.ban_t > 0:
            self.ban_t -= dt
            if self.ban_t <= 0:
                self.banner.text = ''
        for m in self.feed:
            m[1] -= dt
        self.feed = [m for m in self.feed if m[1] > 0]
        self.acc += dt
        if self.acc < .1:
            return
        self.acc = 0
        self.rafraichir()

    def rafraichir(self):
        P, p = E.partie, E.joueur
        if P is None or p is None:
            return
        self.t_feed.text = '\n'.join(m[0] for m in self.feed)
        for e in [self.mm, self.pt_moi]:
            e.enabled = P.en_cours
        if not P.en_cours:
            for t in (self.t_timer, self.t_phase, self.t_score, self.t_titan, self.t_hp, self.t_ammo,
                      self.t_arme, self.t_info, self.t_etat):
                t.text = ''
            for b in (self.b_hp, self.b_arm):
                b.scale_x = 0
            return
        reste = max(0, E.DUREE_PARTIE - P.t)
        self.t_timer.text = f'{int(reste // 60):02d}:{int(reste % 60):02d}'
        self.t_phase.text = 'NUIT - zombies enrages' if P.nuit else \
            f'JOUR - la nuit tombe dans {int(max(0, E.DUREE_JOUR - P.t))}s'
        lignes = []
        for q in sorted(E.pilotes, key=lambda q: -q.score):
            etat = 'ELIM' if q.elimine else ('...' if not q.vivant else '')
            lignes.append(f"{'> ' if q is p else '  '}{q.nom}  {int(q.score)} pts  {etat}")
        self.t_score.text = '\n'.join(lignes) + f'\nZombies : {len(E.zombies)}'

        if P.pause:
            self.t_etat.text = 'PAUSE'
        elif p.elimine and not P.fini:
            self.t_etat.text = 'ELIMINE - spectateur\n[R] relancer une partie'
        elif P.fini:
            self.t_etat.text = P.resultat + '\n[R] rejouer'
        elif not p.vivant:
            self.t_etat.text = f'MORT - reapparition... (-{E.COUT_RESPAWN} pts)'
        else:
            self.t_etat.text = ''

        a = p.arme_active() if p.armes else None
        if p.mode == 'titan':
            self.t_titan.text = '[E] EJECTION'
            self.t_hp.text = f'TITAN {int(p.titan_hp)}'
            self.b_hp.scale_x = .32 * max(0, min(1, p.titan_hp / 400))
            self.b_hp.color = color.orange
            self.b_arm.scale_x = 0
        else:
            t = p.titan
            if t is None or not t.vivant:
                if p.titan_cd > 0:
                    self.t_titan.text = f'TITAN PRET DANS {int(p.titan_cd) + 1}s'
                elif p.score >= E.COUT_TITAN:
                    self.t_titan.text = f'[F] APPELER LE TITAN (-{E.COUT_TITAN} pts)'
                else:
                    self.t_titan.text = f'TITAN : {E.COUT_TITAN} pts requis'
            elif t.state == 'falling':
                self.t_titan.text = 'TITANFALL EN COURS...'
            elif distance(p.position, t.position) < 8:
                self.t_titan.text = '[E] EMBARQUER'
            else:
                self.t_titan.text = 'TON TITAN T\'ATTEND'
            fr = max(0, min(1, p.hp / max(1, p.hp_max)))
            self.t_hp.text = f'PV {int(p.hp)}   ARMURE {int(p.armure)}'
            self.b_hp.scale_x = .32 * fr
            self.b_hp.color = Color(1 - fr, .4 + .6 * fr, .1, 1)
            self.b_arm.scale_x = .32 * min(1, p.armure / 50)
        if a is not None:
            self.t_arme.text = a.nom
            if a.rech > 0:
                self.t_ammo.text = 'RECHARGE'
            elif a.reserve is None:
                self.t_ammo.text = f'{a.munitions} / INF'
            else:
                self.t_ammo.text = f'{a.munitions} / {a.reserve}'
        self.t_info.text = f'{p.nb_tactique}x {p.tactique}' if p.mode == 'pilot' else ''
        self.maj_minimap(p)

    def maj_minimap(self, p):
        k = MM_TAILLE / (2 * E.DEMI_MAP)

        def pos(o):
            return (MM_POS.x + o.x * k, MM_POS.y + o.z * k)
        self.pt_moi.position = (*pos(p), -.04)
        self.pt_moi.rotation_z = -p.rotation_y
        autres = [q for q in E.pilotes if q is not p and q.vivant and not q.elimine
                  and math.hypot(q.x - p.x, q.z - p.z) < 80]
        for i, e in enumerate(self.pts_pil):
            e.enabled = i < len(autres)
            if e.enabled:
                e.position, e.color = (*pos(autres[i]), -.03), autres[i].couleur
        proches = [z for z in E.zombies if math.hypot(z.x - p.x, z.z - p.z) < 60]
        for i, e in enumerate(self.pts_zom):
            e.enabled = i < len(proches)
            if e.enabled:
                e.position = (*pos(proches[i]), -.02)
        t = p.titan
        self.pt_titan.enabled = bool(t is not None and t.vivant and t.state == 'ready')
        if self.pt_titan.enabled:
            self.pt_titan.position = (*pos(t), -.03)
