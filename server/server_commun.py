import json
import socket

PORT = 12345
LARGEUR, HAUTEUR = 1000, 700
TICK = 30                      # mises à jour serveur par seconde
RAYON_JOUEUR = 16


def envoyer(sock, obj):
    sock.sendall((json.dumps(obj, separators=(',', ':')) + '\n').encode('utf-8'))


def ip_locale():
    """Adresse LAN de cette machine (à donner aux autres joueurs)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))       # aucun paquet n'est réellement envoyé
        return s.getsockname()[0]
    except OSError:
        return '127.0.0.1'
    finally:
        s.close()