import argparse
import json
import socket
import sys
import threading
import time

import pygame

from server_commun import *

COULEURS = [(231, 76, 60), (52, 152, 219), (46, 204, 113), (241, 196, 15),
            (155, 89, 182), (230, 126, 34), (26, 188, 156), (236, 240, 241)]


class Reseau:
    """Connexion TCP + thread de réception : garde toujours le dernier état reçu."""

    def __init__(self, hote, port, nom):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((hote, port))
        self.sock.settimeout(None)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.id, self.etat, self.connecte = None, {'joueurs': [], 'balles': []}, True
        threading.Thread(target=self.recevoir, daemon=True).start()
        envoyer(self.sock, {'t': 'hello', 'nom': nom})

    def recevoir(self):
        try:
            for ligne in self.sock.makefile('r', encoding='utf-8'):
                m = json.loads(ligne)
                if m['t'] == 'welcome':
                    self.id = m['id']
                elif m['t'] == 'etat':
                    self.etat = m
        except (OSError, ValueError):
            pass
        self.connecte = False

    def envoyer_input(self, dx, dy, tir):
        try:
            envoyer(self.sock, {'t': 'input', 'dx': dx, 'dy': dy, 'tir': tir})
        except OSError:
            self.connecte = False


def main():
    p = argparse.ArgumentParser()
    p.add_argument('hote', nargs='?', default='localhost')
    p.add_argument('--port', type=int, default=PORT)
    p.add_argument('--nom', default='Joueur')
    a = p.parse_args()

    try:
        reseau = Reseau(a.hote, a.port, a.nom)
    except OSError as e:
        sys.exit(f"Impossible de joindre {a.hote}:{a.port} ({e})")

    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption(f"Multijoueur - {a.nom}")
    police = pygame.font.SysFont(None, 22)
    horloge, dernier_envoi, precedent = pygame.time.Clock(), 0, None

    while reseau.connecte:
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                reseau.connecte = False
        if not reseau.connecte:
            break

        k = pygame.key.get_pressed()
        dx = (k[pygame.K_d] or k[pygame.K_RIGHT]) - (k[pygame.K_q] or k[pygame.K_a] or k[pygame.K_LEFT])
        dy = (k[pygame.K_s] or k[pygame.K_DOWN]) - (k[pygame.K_z] or k[pygame.K_w] or k[pygame.K_UP])
        tir = list(pygame.mouse.get_pos()) if pygame.mouse.get_pressed()[0] else None
        cmd = (int(dx), int(dy), tuple(tir) if tir else None)
        if cmd != precedent or time.time() - dernier_envoi > .1:     # n'envoie que si ça change
            reseau.envoyer_input(dx, dy, tir)
            precedent, dernier_envoi = cmd, time.time()

        ecran.fill((25, 28, 35))
        etat = reseau.etat
        for bx, by in etat['balles']:
            pygame.draw.circle(ecran, (255, 235, 130), (bx, by), 4)
        for id, nom, x, y, hp, score in etat['joueurs']:
            if hp <= 0:
                continue
            col = COULEURS[id % len(COULEURS)]
            pygame.draw.circle(ecran, col, (x, y), RAYON_JOUEUR)
            if id == reseau.id:
                pygame.draw.circle(ecran, (255, 255, 255), (x, y), RAYON_JOUEUR + 3, 2)
            pygame.draw.rect(ecran, (80, 0, 0), (x - 20, y - 28, 40, 5))
            pygame.draw.rect(ecran, (0, 200, 0), (x - 20, y - 28, 40 * hp / 100, 5))
            t = police.render(nom, True, (230, 230, 230))
            ecran.blit(t, (x - t.get_width() // 2, y - 46))

        # tableau des scores
        for i, (id, nom, x, y, hp, score) in enumerate(sorted(etat['joueurs'], key=lambda j: -j[5])):
            ecran.blit(police.render(f"{nom} : {score}", True, COULEURS[id % len(COULEURS)]), (10, 10 + i * 20))
        pygame.display.flip()
        horloge.tick(60)

    pygame.quit()
    print("Déconnecté.")


if __name__ == "__main__":
    main()