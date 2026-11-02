import argparse
import json
import math
import random
import socket
import threading
import time

from server_commun import *

VITESSE = 220            # px/s
VITESSE_BALLE = 650
DEGATS = 20
CADENCE = .3             # secondes entre deux tirs
VIE_BALLE = 1.5
RESPAWN = 3
VIE_MAX = 100
MAX_JOUEURS = 8


class Joueur:
    def __init__(self, id, sock):
        self.id, self.sock, self.nom = id, sock, f'Joueur{id}'
        self.verrou_envoi = threading.Lock()
        self.dx = self.dy = 0
        self.tir = None
        self.dernier_tir = 0
        self.score = 0
        self.reapparaitre()

    def reapparaitre(self):
        self.x = random.randint(60, LARGEUR - 60)
        self.y = random.randint(60, HAUTEUR - 60)
        self.hp, self.mort_jusqu = VIE_MAX, 0

    @property
    def vivant(self):
        return self.hp > 0


class Serveur:
    def __init__(self, hote, port):
        self.joueurs, self.balles = {}, []          # balles : [x, y, vx, vy, vie, id_tireur]
        self.verrou = threading.Lock()
        self.prochain_id = 1
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((hote, port))
        self.sock.listen(MAX_JOUEURS)

    # ---------- réseau ----------
    def accepter(self):
        while True:
            conn, adr = self.sock.accept()
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            with self.verrou:
                if len(self.joueurs) >= MAX_JOUEURS:
                    conn.close()
                    continue
                j = Joueur(self.prochain_id, conn)
                self.prochain_id += 1
                self.joueurs[j.id] = j
            print(f"+ {adr[0]} connecté (joueur {j.id}) - {len(self.joueurs)} en ligne")
            try:
                envoyer(conn, {'t': 'welcome', 'id': j.id, 'largeur': LARGEUR, 'hauteur': HAUTEUR})
            except OSError:
                self.retirer(j)
                continue
            threading.Thread(target=self.ecouter, args=(j,), daemon=True).start()

    def ecouter(self, j):
        """Un thread par client : lit ses messages (une ligne JSON chacun)."""
        try:
            for ligne in j.sock.makefile('r', encoding='utf-8'):
                try:
                    m = json.loads(ligne)
                except ValueError:
                    continue
                if m.get('t') == 'hello':
                    j.nom = str(m.get('nom', j.nom))[:12] or j.nom
                elif m.get('t') == 'input':
                    j.dx = max(-1, min(1, int(m.get('dx', 0))))
                    j.dy = max(-1, min(1, int(m.get('dy', 0))))
                    j.tir = m.get('tir')
        except (OSError, ValueError, TypeError):
            pass
        self.retirer(j)

    def retirer(self, j):
        with self.verrou:
            if self.joueurs.pop(j.id, None) is None:
                return
        try:
            j.sock.close()
        except OSError:
            pass
        print(f"- {j.nom} déconnecté - {len(self.joueurs)} en ligne")

    def diffuser(self):
        with self.verrou:
            etat = {'t': 'etat',
                    'joueurs': [[j.id, j.nom, round(j.x), round(j.y), j.hp, j.score]
                                for j in self.joueurs.values()],
                    'balles': [[round(b[0]), round(b[1])] for b in self.balles]}
            clients = list(self.joueurs.values())
        for j in clients:
            try:
                with j.verrou_envoi:
                    envoyer(j.sock, etat)
            except OSError:
                self.retirer(j)

    # ---------- simulation ----------
    def mettre_a_jour(self, dt):
        now = time.time()
        with self.verrou:
            for j in self.joueurs.values():
                if not j.vivant:
                    if now >= j.mort_jusqu:
                        j.reapparaitre()
                    continue
                n = math.hypot(j.dx, j.dy) or 1
                j.x = max(RAYON_JOUEUR, min(LARGEUR - RAYON_JOUEUR, j.x + j.dx / n * VITESSE * dt))
                j.y = max(RAYON_JOUEUR, min(HAUTEUR - RAYON_JOUEUR, j.y + j.dy / n * VITESSE * dt))
                if j.tir and now - j.dernier_tir >= CADENCE:
                    ang = math.atan2(j.tir[1] - j.y, j.tir[0] - j.x)
                    self.balles.append([j.x, j.y, math.cos(ang) * VITESSE_BALLE,
                                        math.sin(ang) * VITESSE_BALLE, VIE_BALLE, j.id])
                    j.dernier_tir = now

            restantes = []
            for b in self.balles:
                b[0] += b[2] * dt
                b[1] += b[3] * dt
                b[4] -= dt
                if b[4] <= 0 or not (0 <= b[0] <= LARGEUR and 0 <= b[1] <= HAUTEUR):
                    continue
                touche = False
                for j in self.joueurs.values():
                    if j.vivant and j.id != b[5] and math.hypot(j.x - b[0], j.y - b[1]) < RAYON_JOUEUR + 4:
                        j.hp -= DEGATS
                        touche = True
                        if j.hp <= 0:
                            j.mort_jusqu = now + RESPAWN
                            tireur = self.joueurs.get(b[5])
                            if tireur:
                                tireur.score += 1
                        break
                if not touche:
                    restantes.append(b)
            self.balles = restantes

    def boucle(self):
        dt_tick, dernier = 1 / TICK, time.time()
        while True:
            time.sleep(max(0, dt_tick - (time.time() - dernier)))
            now = time.time()
            self.mettre_a_jour(now - dernier)
            dernier = now
            self.diffuser()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', type=int, default=PORT)
    p.add_argument('--local', action='store_true', help="n'accepter que cette machine")
    a = p.parse_args()
    serveur = Serveur('127.0.0.1' if a.local else '0.0.0.0', a.port)
    print(f"Serveur démarré sur le port {a.port}")
    print(f"  Même machine : localhost\n  Réseau local : {ip_locale()}")
    threading.Thread(target=serveur.accepter, daemon=True).start()
    try:
        serveur.boucle()
    except KeyboardInterrupt:
        print("Arrêt du serveur.")


if __name__ == "__main__":
    main()