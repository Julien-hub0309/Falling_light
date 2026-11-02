"""graphismes.py - Qualité graphique, éclairage jour/nuit, brouillard, textures
procédurales et helper solide() qui crée une entité du monde éclairée.

QUALITE : 'bas'   = couleurs plates (PC faible)
          'moyen' = éclairage soleil + ambiance + brouillard (défaut)
          'haut'  = moyen + anti-aliasing FXAA + plus de particules"""
import numpy as np
from ursina import *
from PIL import Image, ImageDraw

QUALITE = 'moyen'
NIVEAUX = ('bas', 'moyen', 'haut')
FOG = (80, 340)
SOLEIL_DIR = Vec3(-.5, -1.1, -.6)
_shader = None
_shader_emi = None
disque = None

_VERT = '''#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec4 p3d_Vertex; in vec3 p3d_Normal; in vec2 p3d_MultiTexCoord0; in vec4 p3d_Color;
uniform vec2 texture_scale; uniform vec2 texture_offset;
out vec2 uvs; out vec3 wn; out vec3 wp; out vec4 vc;
void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    uvs = p3d_MultiTexCoord0 * texture_scale + texture_offset;
    wn = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
    wp = (p3d_ModelMatrix * p3d_Vertex).xyz;
    vc = p3d_Color;
}'''
_FRAG = '''#version 140
uniform sampler2D p3d_Texture0; uniform vec4 p3d_ColorScale;
in vec2 uvs; in vec3 wn; in vec3 wp; in vec4 vc;
uniform vec3 sun_dir; uniform vec3 sun_color; uniform vec3 amb_color;
uniform vec3 camera_world_position; uniform vec4 fog_color; uniform vec2 fog_range;
out vec4 fragColor;
void main() {
    vec4 t = texture(p3d_Texture0, uvs);
    vec4 c = t * p3d_ColorScale * vc;
    vec3 n = normalize(wn);
    float ndl = max(dot(n, -sun_dir), 0.0);
    float sky = 0.5 + 0.5 * n.y;
    float nuit = 1.0 - clamp(length(amb_color) / 1.1, 0.0, 1.0);
    float em = step(0.82, t.r) * step(0.6, t.g) * step(t.b, 0.55);   // fenêtres allumées
    vec3 eclaire = c.rgb * (amb_color * (0.72 + 0.28 * sky) + sun_color * ndl);
    c.rgb = mix(eclaire, t.rgb * vc.rgb * 1.15, em * nuit);
    float d = length(wp - camera_world_position);
    float f = clamp((d - fog_range.x) / (fog_range.y - fog_range.x), 0.0, 1.0);
    c.rgb = mix(c.rgb, fog_color.rgb, f);
    fragColor = c;
}'''

JOUR = dict(soleil=(.95, .88, .72), amb=(.66, .68, .74), ciel=(1, 1, 1), brume=(.64, .74, .85), disque=(1, .92, .55))
NUIT = dict(soleil=(.20, .26, .45), amb=(.18, .20, .32), ciel=(.10, .12, .28), brume=(.03, .04, .09), disque=(.78, .84, 1))


def _mix(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


_FRAG_EMI = '''#version 140
uniform sampler2D p3d_Texture0; uniform vec4 p3d_ColorScale;
in vec2 uvs; in vec3 wn; in vec3 wp; in vec4 vc;
uniform vec3 camera_world_position; uniform vec4 fog_color; uniform vec2 fog_range;
uniform vec3 amb_color;
out vec4 fragColor;
void main() {
    vec4 c = texture(p3d_Texture0, uvs) * p3d_ColorScale * vc;
    float nuit = 1.0 - clamp(length(amb_color) / 1.1, 0.0, 1.0);
    c.rgb *= 0.55 + 0.9 * nuit;
    float d = length(wp - camera_world_position);
    float f = clamp((d - fog_range.x) / (fog_range.y - fog_range.x), 0.0, 1.0);
    c.rgb = mix(c.rgb, fog_color.rgb, f);
    fragColor = c;
}'''


def appliquer_emissif(e):
    if _shader_emi is not None:
        e.shader = _shader_emi


def init():
    """À appeler juste après Ursina()."""
    global _shader, _shader_emi, disque
    Entity.default_shader = None            # pas de mise à jour de shader par entité (coûteux)
    if QUALITE != 'bas':
        _shader = Shader(name='monde', language=Shader.GLSL, vertex=_VERT, fragment=_FRAG,
                         default_input={'texture_scale': Vec2(1, 1), 'texture_offset': Vec2(0, 0)})
        _shader_emi = Shader(name='monde_emi', language=Shader.GLSL, vertex=_VERT, fragment=_FRAG_EMI,
                             default_input={'texture_scale': Vec2(1, 1), 'texture_offset': Vec2(0, 0)})
        scene.set_shader_input('sun_dir', SOLEIL_DIR.normalized())
        scene.set_shader_input('fog_range', Vec2(*FOG))
        maj_jour(0)
    scene.fog_density = FOG
    disque = Entity(model='sphere', scale=26, color=color.yellow)
    disque.setFogOff()
    _Maj()
    if QUALITE == 'haut':
        try:
            from ursina.shaders import fxaa_shader
            camera.shader = fxaa_shader
        except Exception as e:
            print('FXAA indisponible :', e)


def solide(**kw):
    """Entité du monde (éclairée si la qualité le permet)."""
    kw.setdefault('ignore', True)           # purement visuel : pas d'update() inutile
    e = Entity(**kw)
    if _shader is not None:
        e.shader = _shader
    return e


def maj_jour(k):
    """k = 0 plein jour -> 1 pleine nuit : lumières, brouillard, ciel, soleil/lune."""
    s, a = _mix(JOUR['soleil'], NUIT['soleil'], k), _mix(JOUR['amb'], NUIT['amb'], k)
    brume = _mix(JOUR['brume'], NUIT['brume'], k)
    if _shader is not None:
        scene.set_shader_input('sun_color', Vec3(*s))
        scene.set_shader_input('amb_color', Vec3(*a))
        scene.set_shader_input('fog_color', Color(*brume, 1))
    scene.fog_color = Color(*brume, 1)
    if disque is not None:
        disque.color = Color(*_mix(JOUR['disque'], NUIT['disque'], k), 1)
    return _mix(JOUR['ciel'], NUIT['ciel'], k)


class _Maj(Entity):
    """Met à jour chaque frame la position caméra (brouillard) et du disque soleil/lune."""
    def update(self):
        if _shader is not None:
            scene.set_shader_input('camera_world_position', camera.world_position)
        if disque is not None:
            disque.position = camera.world_position + Vec3(.5, .55, .65).normalized() * 280


# ---- textures procédurales -------------------------------------------------------
_cache = {}


def _bruit(w, h, base, amp):
    n = np.random.randint(-amp, amp + 1, (h, w, 1))
    return np.clip(np.array(base)[None, None, :] + n, 0, 255).astype('uint8')


def _texture(img, mip=True):
    t = Texture(img)
    if mip:
        t.filtering = 'mipmap'
    return t


def texture(nom):
    if nom in _cache:
        return _cache[nom]
    rng = np.random.RandomState(7)
    np.random.seed(7)
    if nom == 'facade':      # béton + 4x4 fenêtres (quelques-unes allumées / cassées)
        img = Image.fromarray(_bruit(256, 256, (150, 148, 144), 14))
        d = ImageDraw.Draw(img)
        for i in range(4):
            for j in range(4):
                x, y = i * 64 + 14, j * 64 + 12
                r = rng.rand()
                col = (255, 205, 110) if r < .13 else ((12, 14, 18) if r < .24 else (38, 52, 72))
                d.rectangle([x - 3, y - 3, x + 39, y + 45], fill=(95, 92, 88))
                d.rectangle([x, y, x + 36, y + 42], fill=col)
                if r >= .24:
                    d.line([x + 18, y, x + 18, y + 42], fill=(95, 92, 88), width=2)
                    d.line([x, y + 21, x + 36, y + 21], fill=(95, 92, 88), width=2)
        for j in range(4):
            d.line([0, j * 64 + 58, 256, j * 64 + 58], fill=(120, 117, 112), width=3)
        t = _texture(img)
    elif nom == 'sol':
        arr = _bruit(128, 128, (88, 86, 80), 18)
        for _ in range(14):
            x, y = rng.randint(0, 128), rng.randint(0, 128)
            arr[y, max(0, x - 20):x + 20] = (50, 48, 46)
        t = _texture(Image.fromarray(arr))
    elif nom == 'route':     # asphalte, bandes de rive blanches, pointillés jaunes
        arr = _bruit(64, 128, (52, 53, 58), 10)
        img = Image.fromarray(arr)
        d = ImageDraw.Draw(img)
        d.rectangle([3, 0, 5, 128], fill=(190, 190, 190))
        d.rectangle([58, 0, 60, 128], fill=(190, 190, 190))
        for y in range(0, 128, 32):
            d.rectangle([30, y, 33, y + 16], fill=(215, 175, 40))
        t = _texture(img)
    elif nom == 'metal':     # conteneurs / tôle ondulée
        arr = _bruit(64, 64, (200, 200, 200), 10)
        arr[:, ::8] = (arr[:, ::8] * .72).astype('uint8')
        t = _texture(Image.fromarray(arr))
    elif nom == 'brique':    # briques rouges + fenêtres
        arr = _bruit(256, 256, (150, 78, 62), 16)
        img = Image.fromarray(arr)
        d = ImageDraw.Draw(img)
        for y in range(0, 256, 8):
            d.line([0, y, 256, y], fill=(100, 70, 60), width=1)
            for x in range((y // 8 % 2) * 8, 256, 16):
                d.line([x, y, x, y + 8], fill=(100, 70, 60), width=1)
        for i in range(4):
            for j in range(4):
                x, y = i * 64 + 16, j * 64 + 10
                r = rng.rand()
                col = (255, 205, 110) if r < .12 else ((10, 12, 16) if r < .25 else (45, 58, 78))
                d.rectangle([x - 3, y - 3, x + 35, y + 47], fill=(215, 205, 190))
                d.rectangle([x, y, x + 32, y + 44], fill=col)
        t = _texture(img)
    elif nom == 'verre':     # tour de bureaux : mur-rideau bleuté
        arr = _bruit(256, 256, (62, 92, 118), 10)
        img = Image.fromarray(arr)
        d = ImageDraw.Draw(img)
        for i in range(0, 257, 32):
            d.line([i, 0, i, 256], fill=(30, 40, 52), width=2)
        for j in range(0, 257, 64):
            d.line([0, j, 256, j], fill=(30, 40, 52), width=4)
        for i in range(8):
            for j in range(4):
                r = rng.rand()
                if r < .14:
                    d.rectangle([i * 32 + 3, j * 64 + 6, i * 32 + 29, j * 64 + 58], fill=(255, 215, 130))
                elif r < .3:
                    d.rectangle([i * 32 + 3, j * 64 + 6, i * 32 + 29, j * 64 + 58], fill=(20, 28, 40))
        t = _texture(img)
    elif nom == 'trottoir':
        arr = _bruit(128, 128, (128, 126, 120), 10)
        arr[::32, :] = (88, 86, 82)
        arr[:, ::32] = (88, 86, 82)
        t = _texture(Image.fromarray(arr))
    elif nom == 'herbe':
        t = _texture(Image.fromarray(_bruit(128, 128, (84, 92, 52), 26)))
    elif nom == 'bois':
        arr = _bruit(64, 64, (110, 78, 50), 12)
        arr[:, ::6] = (arr[:, ::6] * .75).astype('uint8')
        t = _texture(Image.fromarray(arr))
    elif nom == 'toit':
        t = _texture(Image.fromarray(_bruit(64, 64, (140, 136, 130), 14)))
    else:
        t = 'white_cube'
    _cache[nom] = t
    return t
