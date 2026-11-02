import os
import sys
import atexit
import getpass
import socket
import subprocess
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "falling_light.log"
os.chdir(ROOT)                                   # config.json, assets... toujours relatifs au jeu
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _relancer_dans_venv():
    """Si le jeu est lancé avec le Python système alors que .venv existe (installateur), on bascule dessus."""
    if os.environ.get("FALLING_LIGHT_VENV") == "1":
        return
    venv = ROOT / ".venv"
    py = venv / "Scripts" / "python.exe" if os.name == "nt" else venv / "bin" / "python"
    if py.exists() and Path(sys.prefix).resolve() != venv.resolve():
        env = dict(os.environ, FALLING_LIGHT_VENV="1")
        args = [str(py), str(ROOT / "titanfall.py"), *sys.argv[1:]]
        if os.name == "nt":
            sys.exit(subprocess.call(args, env=env))
        os.execve(str(py), args, env)


if __name__ == "__main__":
    _relancer_dans_venv()

try:
    from ursina import *
except ImportError:
    sys.exit("Ursina n'est pas installé. Lancez d'abord :  python installateur.py")

import random

PORT_DEFAUT = 12345
DOSSIER_SERVEUR = ROOT / "server"

# ---------------------------------------------------------------- thème ---
def rgb(r, g, b, a=1):
    return Color(r / 255, g / 255, b / 255, a)


def teinte(c, k, a=1):
    return Color(c[0] * k, c[1] * k, c[2] * k, a)


FOND = rgb(7, 9, 18)
CYAN, ORANGE, VERT = rgb(0, 190, 255), rgb(255, 140, 40), rgb(60, 220, 120)
GRIS, ROUGE, BLANC = rgb(140, 150, 168), rgb(255, 95, 95), rgb(240, 244, 250)


# ------------------------------------------------------------- utilitaires ---
def journaliser(texte):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(texte + "\n")
    except OSError:
        pass


def ip_locale():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def pseudo_defaut():
    try:
        return getpass.getuser()[:12] or "Joueur"
    except Exception:
        return "Joueur"


def lancer(script, *args, journal):
    """Lance un script du dossier server/ dans un processus séparé (sortie dans server/<journal>.log)."""
    chemin = DOSSIER_SERVEUR / script
    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")
    sortie = open(DOSSIER_SERVEUR / f"{journal}.log", "a", encoding="utf-8")
    return subprocess.Popen([sys.executable, str(chemin), *map(str, args)], cwd=DOSSIER_SERVEUR,
                            stdout=sortie, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)


def analyser_adresse(texte):
    """'192.168.1.20' ou '192.168.1.20:5000' -> (hote, port). Lève ValueError si invalide."""
    texte = texte.strip()
    if not texte:
        raise ValueError("Entrez l'adresse IP du serveur.")
    hote, port = texte, PORT_DEFAUT
    if texte.count(":") == 1:
        hote, p = texte.split(":")
        if not p.isdigit() or not (1 <= int(p) <= 65535):
            raise ValueError("Port invalide (1 à 65535).")
        port = int(p)
    if not hote.strip():
        raise ValueError("Adresse invalide.")
    return hote.strip(), port


# ------------------------------------------------------------- composants ---
class Bouton(Button):
    def __init__(self, parent, texte, couleur, action, y, w=.5, h=.07):
        super().__init__(parent=parent, text=texte, y=y, scale=(w, h), radius=.25,
                         color=teinte(couleur, .22, .95), highlight_color=teinte(couleur, .5),
                         pressed_color=teinte(couleur, .75), highlight_scale=1.03, on_click=action)
        self.barre = Entity(parent=self, model="quad", color=couleur, scale=(.012 / w, .62),
                            x=-.5 + .03 / w, z=-.01)


def etiquette(parent, texte, y, couleur=GRIS, echelle=.9, x=0):
    return Text(parent=parent, text=texte, y=y, x=x, origin=(0, 0), scale=echelle, color=couleur)


def champ(parent, y, valeur, limite=24, autorises=None):
    c = InputField(parent=parent, y=y, character_limit=limite, scale=(.5, .06))
    c.text = valeur
    if autorises:
        c.limit_content_to = autorises
    return c


# ------------------------------------------------------------------- menu ---
class Menu(Entity):
    IP_AUTORISES = "0123456789:.-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self):
        super().__init__(parent=camera.ui)
        window.color = FOND
        for n in ("exit_button", "cog_button"):
            b = getattr(window, n, None)
            if b is not None:
                b.enabled = False
        self.serveur, self.t_serveur = None, 0
        atexit.register(self._tuer_serveur)

        # décor : lueur + pluie de lumière
        Entity(parent=self, model="quad", scale=(3, 1.5), color=FOND, z=3)
        for i in range(8):                                           # lueur dégradée en haut
            Entity(parent=self, model="quad", scale=(3, .16 * (i + 1)), y=.5 - .08 * (i + 1),
                   color=Color(0, .35, .55, .022), z=2.9)
        self.etat_fenetre = {n: getattr(getattr(window, n, None), "enabled", None)
                             for n in ("fps_counter", "entity_counter", "collider_counter")}
        for n in self.etat_fenetre:
            if self.etat_fenetre[n] is not None:
                getattr(window, n).enabled = False
        self.pluie = []
        for _ in range(55):
            e = Entity(parent=self, model="quad", z=2.5, x=random.uniform(-.9, .9), y=random.uniform(-.6, .6),
                       scale=(random.choice((.002, .003, .004)), random.uniform(.05, .22)),
                       color=Color(.1, .75, 1, random.uniform(.12, .5)))
            e.vitesse = random.uniform(.12, .42)
            self.pluie.append(e)

        # titre
        self.logo = None
        try:
            from PIL import Image
            if icone.exists():
                self.logo = Entity(parent=self, model="quad", texture=Texture(Image.open(icone)),
                                   scale=.13, x=-.78, y=.42)
        except Exception:
            pass
        Text(parent=self, text="FALLING LIGHT", origin=(0, 0), y=.33, scale=3.4, color=BLANC)
        Entity(parent=self, model="quad", y=.215, scale=(.55, .003), color=Color(0, .75, 1, .6))
        etiquette(self, "Python • Ursina", -.465, rgb(80, 90, 105), .75)

        self.pages = {}
        self.historique = []
        self._page_accueil()
        self._page_lan()
        self._page_rejoindre()
        self._page_heberger()
        self.aller("accueil", memoriser=False)

    # ---- navigation ----
    def nouvelle_page(self, nom):
        p = Entity(parent=self)
        self.pages[nom] = p
        return p

    def aller(self, nom, memoriser=True):
        if memoriser and getattr(self, "courante", None):
            self.historique.append(self.courante)
        self.courante = nom
        for k, p in self.pages.items():
            p.enabled = (k == nom)
        for s in getattr(self, "statuts", {}).values():
            s.text = ""

    def retour(self):
        self.aller(self.historique.pop() if self.historique else "accueil", memoriser=False)

    def statut(self, page, texte, couleur=ROUGE):
        s = self.statuts[page]
        s.text, s.color = texte, couleur

    def input(self, key):
        if key == "escape" and self.courante != "accueil":
            self.retour()

    # ---- pages ----
    def _page_accueil(self):
        p = self.nouvelle_page("accueil")
        Bouton(p, "SOLO", VERT, self.solo, y=.07)
        etiquette(p, "Affrontez les IA et les zombies", .07 - .062)
        Bouton(p, "MULTIJOUEUR LAN", CYAN, lambda: self.aller("lan"), y=-.1)
        etiquette(p, "Hébergez ou rejoignez une partie sur le réseau local", -.1 - .062)
        Bouton(p, "QUITTER", GRIS, application.quit, y=-.27, h=.06)

    def _page_lan(self):
        p = self.nouvelle_page("lan")
        etiquette(p, "MODE LAN", .12, BLANC, 1.5)
        Bouton(p, "HÉBERGER UNE PARTIE", ORANGE, lambda: self.aller("heberger"), y=-.0)
        etiquette(p, "Vous lancez le serveur, les autres se connectent à vous", -.062)
        Bouton(p, "REJOINDRE UNE PARTIE", CYAN, lambda: self.aller("rejoindre"), y=-.17)
        etiquette(p, "Entrez l'adresse IP de l'hôte", -.17 - .062)
        Bouton(p, "RETOUR", GRIS, self.retour, y=-.33, h=.06)

    def _page_rejoindre(self):
        p = self.nouvelle_page("rejoindre")
        self.statuts = getattr(self, "statuts", {})
        etiquette(p, "REJOINDRE UNE PARTIE", .13, BLANC, 1.5)
        etiquette(p, "Pseudo", .075, GRIS, .85, x=-.25).origin = (-.5, 0)
        self.j_nom = champ(p, .03, pseudo_defaut(), 12)
        etiquette(p, "Adresse du serveur  (ex. 192.168.1.20  ou  192.168.1.20:5000)", -.035, GRIS, .85, x=-.25).origin = (-.5, 0)
        self.j_ip = champ(p, -.085, "", 40, self.IP_AUTORISES)
        self.j_nom.next_field, self.j_ip.next_field = self.j_ip, self.j_nom
        self.j_ip.on_submit, self.j_ip.submit_on = self.rejoindre, ["enter"]
        self.statuts["rejoindre"] = etiquette(p, "", -.15, ROUGE, .9)
        Bouton(p, "CONNEXION", CYAN, self.rejoindre, y=-.24)
        Bouton(p, "RETOUR", GRIS, self.retour, y=-.34, h=.055)

    def _page_heberger(self):
        p = self.nouvelle_page("heberger")
        etiquette(p, "HÉBERGER UNE PARTIE", .13, BLANC, 1.5)
        # état 1 : avant le lancement
        a = self.h_avant = Entity(parent=p)
        etiquette(a, "Pseudo", .075, GRIS, .85, x=-.25).origin = (-.5, 0)
        self.h_nom = champ(a, .03, pseudo_defaut(), 12)
        etiquette(a, "Le serveur écoute sur le port %d (autorisez-le dans le pare-feu)." % PORT_DEFAUT, -.05, GRIS, .8)
        Bouton(a, "LANCER LE SERVEUR", ORANGE, self.lancer_serveur, y=-.16)
        Bouton(a, "RETOUR", GRIS, self.retour, y=-.28, h=.055)
        # état 2 : serveur actif
        b = self.h_apres = Entity(parent=p, enabled=False)
        etiquette(b, "• SERVEUR ACTIF", .07, VERT, 1.2)
        etiquette(b, "Communiquez cette adresse aux autres joueurs :", .0, GRIS, .85)
        self.h_adresse = etiquette(b, "", -.055, BLANC, 2)
        etiquette(b, "Le serveur s'arrête quand vous fermez cette fenêtre.", -.115, GRIS, .75)
        Bouton(b, "JOUER (me connecter)", VERT, self.jouer_chez_moi, y=-.2)
        Bouton(b, "ARRÊTER LE SERVEUR", ROUGE, self.arreter_serveur, y=-.3, h=.06)
        self.statuts = getattr(self, "statuts", {})
        self.statuts["heberger"] = etiquette(p, "", -.4, ROUGE, .85)

    # ---- actions ----
    def solo(self):
        self.arreter_serveur()
        for n, etat in self.etat_fenetre.items():
            if etat is not None:
                getattr(window, n).enabled = etat
        destroy(self)
        try:
            demarrer_jeu()
        except Exception:
            tb = traceback.format_exc()
            journaliser(tb)
            print(tb)
            afficher_erreur(tb)

    def rejoindre(self):
        try:
            hote, port = analyser_adresse(self.j_ip.text)
        except ValueError as e:
            return self.statut("rejoindre", str(e))
        nom = self.j_nom.text.strip()[:12] or "Joueur"
        try:                                                       # le serveur répond-il ?
            socket.create_connection((hote, port), timeout=1.5).close()
        except OSError:
            return self.statut("rejoindre", f"Aucun serveur trouvé sur {hote}:{port}")
        try:
            lancer("server_client.py", hote, "--port", port, "--nom", nom, journal="client")
        except Exception as e:
            return self.statut("rejoindre", str(e))
        application.quit()

    def lancer_serveur(self):
        if self.serveur and self.serveur.poll() is None:
            return
        try:
            self.serveur = lancer("server_game.py", "--port", PORT_DEFAUT, journal="serveur")
        except Exception as e:
            return self.statut("heberger", str(e))
        self.t_serveur = 1.2                                       # on vérifie qu'il n'a pas planté
        self.h_avant.enabled, self.h_apres.enabled = False, True
        self.h_adresse.text = f"{ip_locale()}:{PORT_DEFAUT}"

    def jouer_chez_moi(self):
        nom = self.h_nom.text.strip()[:12] or "Joueur"
        try:
            lancer("server_client.py", "127.0.0.1", "--port", PORT_DEFAUT, "--nom", nom, journal="client")
        except Exception as e:
            self.statut("heberger", str(e))

    def _tuer_serveur(self):
        """Arrête le processus serveur (aussi appelé à la fermeture de l'application)."""
        if self.serveur and self.serveur.poll() is None:
            self.serveur.terminate()
            try:
                self.serveur.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.serveur.kill()
        self.serveur = None

    def arreter_serveur(self):
        self._tuer_serveur()
        self.h_avant.enabled, self.h_apres.enabled = True, False

    # ---- animation + surveillance du serveur ----
    def update(self):
        for e in self.pluie:
            e.y -= e.vitesse * time.dt
            if e.y < -.7:
                e.y, e.x = .7, random.uniform(-.9, .9)
        if self.serveur is not None and self.t_serveur > 0:
            self.t_serveur -= time.dt
            if self.t_serveur <= 0 and self.serveur.poll() is not None:
                self.serveur = None
                self.h_avant.enabled, self.h_apres.enabled = True, False
                self.statut("heberger", "Le serveur n'a pas démarré (port déjà utilisé ?). Voir server/serveur.log")


def afficher_erreur(tb):
    derniere = tb.strip().splitlines()[-1][:110]
    Text(parent=camera.ui, origin=(0, 0), y=.1, scale=1.6, color=ROUGE, text="Erreur au lancement du jeu")
    Text(parent=camera.ui, origin=(0, 0), y=0, scale=.9, color=BLANC, text=derniere)
    Text(parent=camera.ui, origin=(0, 0), y=-.08, scale=.8, color=GRIS, text=f"Détails dans {LOG.name}")
    Button(parent=camera.ui, text="QUITTER", scale=(.25, .06), y=-.2, color=teinte(ROUGE, .4), on_click=application.quit)


# =====================================================
# JEU SOLO
# =====================================================

def demarrer_jeu():

    from parametres import config, graphismes as G

    config.charger()

    import etat as E
    from map.map import construire_map
    from bot.joueur import Player
    from bot.ennemie import PiloteIA
    from HUD.hud import HUD
    from partie import Partie
    from classe.choix_classe import MenuClasse
    from parametres.options import OptionsMenu

    window.exit_button.visible = False

    E.ciel = Sky()

    G.init()

    mouse.locked = False

    construire_map()

    E.joueur = Player()

    for nom, col in (
        ('Alpha', color.red),
        ('Bravo', color.orange),
        ('Charlie', color.violet),
        ('Delta', color.green)
    ):
        PiloteIA(nom, col)

    E.hud = HUD()

    E.partie = Partie(E.ciel)

    E.menu = MenuClasse(E.partie.demarrer)

    E.options = OptionsMenu()

    E.partie.ouvrir_menu()


# =====================================================
# APPLICATION
# =====================================================

def main():
    app = Ursina(title="FALLING LIGHT")
    menu = Menu()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        journaliser(tb)
        raise