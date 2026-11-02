"""batch.py - Géométrie statique fusionnée : toutes les boîtes d'une même texture sont
regroupées en UN SEUL maillage (très peu d'appels de rendu, même sur une grande ville).
Les UV sont calculés en coordonnées monde : les fenêtres restent alignées sur les étages."""
from ursina import Mesh, Entity, Vec3, Color
import parametres.graphismes as G

SIGNE = -1         # sens d'enroulement des faces (vérifié par rendu)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


class Batch:
    def __init__(self, nom, tex=None, tuile=8, emissif=False):
        self.nom, self.tex, self.tuile, self.emissif = nom, tex, tuile, emissif
        self.v, self.n, self.uv, self.c, self.t = [], [], [], [], []

    def quad(self, p, n, col, uvs):
        a = (p[1][0] - p[0][0], p[1][1] - p[0][1], p[1][2] - p[0][2])
        b = (p[2][0] - p[0][0], p[2][1] - p[0][1], p[2][2] - p[0][2])
        cr = _cross(a, b)
        if (cr[0] * n[0] + cr[1] * n[1] + cr[2] * n[2]) * SIGNE < 0:      # face vers l'extérieur
            p, uvs = p[::-1], uvs[::-1]
        i = len(self.v)
        self.v += p
        self.n += [n] * 4
        self.uv += uvs
        self.c += [col] * 4
        self.t.append((i, i + 1, i + 2, i + 3))

    def plan(self, x0, x1, z0, z1, y, col, tuile=None, tourne=False, u0=0, v0=0):
        """Face horizontale tournée vers le haut (routes, sol, toits)."""
        ts = tuile or self.tuile
        tu, tv = ts if isinstance(ts, tuple) else (ts, ts)
        p = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
        if tourne:
            uvs = [((z - z0) / tu + u0, (x - x0) / tv + v0) for x, _, z in p]
        else:
            uvs = [((x - x0) / tu + u0, (z - z0) / tv + v0) for x, _, z in p]
        self.quad(p, (0, 1, 0), col, uvs)

    def box(self, x0, x1, y0, y1, z0, z1, col, haut=None, bas=False, col_haut=None):
        """Boîte : 4 flancs dans ce batch, le dessus dans `haut` (autre batch) si fourni."""
        ts = self.tuile
        f = [((x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0), (1, 0, 0), 'z'),
             ((x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0), (-1, 0, 0), 'z'),
             ((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), (0, 0, 1), 'x'),
             ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (0, 0, -1), 'x')]
        for a, b, c, d, n, ax in f:
            p = [a, b, c, d]
            if ax == 'z':
                uvs = [(q[2] / ts, q[1] / ts) for q in p]
            else:
                uvs = [(q[0] / ts, q[1] / ts) for q in p]
            self.quad(p, n, col, uvs)
        cible = haut or self
        cible.plan(x0, x1, z0, z1, y1, col_haut or col, cible.tuile)
        if bas:
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0), col,
                      [(0, 0), (1, 0), (1, 1), (0, 1)])

    def construire(self):
        if not self.v:
            return None
        m = Mesh(vertices=self.v, triangles=self.t, uvs=self.uv, normals=self.n, colors=self.c, static=True)
        e = Entity(model=m, texture=G.texture(self.tex) if self.tex else 'white_cube')
        if self.emissif:
            G.appliquer_emissif(e)
        elif G._shader is not None:
            e.shader = G._shader
        else:
            from ursina.shaders.unlit_with_fog_shader import unlit_with_fog_shader
            e.shader = unlit_with_fog_shader
        return e


class Monde:
    """Registre de batches nommés."""
    def __init__(self):
        self.b = {}

    def batch(self, nom, tex=None, tuile=8, emissif=False):
        if nom not in self.b:
            self.b[nom] = Batch(nom, tex, tuile, emissif)
        return self.b[nom]

    def construire(self):
        return [b.construire() for b in self.b.values()]
