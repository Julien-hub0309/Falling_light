# Falling_light

## Idée amélioration : 

### Multi-joueur local : 

- server.py -> créer un serveur temporaire lie les pc en jeux et leur permet de jouer entre eux
  - server_client -> écoutes et envoie les paramètres a server de jeux
  - server_game.py -> le serveurs qui lie les pc entre eux a lancer pas le gamemaster
 
### Zombie normal + spéciaux : 
- Jour :
  - Zombie en majorité faible, les armes a feu produise du bruit qui attire les zombie spéciaux
  - Zombie normal 150% de vie 80% de vitesse en groupe de 3 ou 4 pour 40 zombie dans une partie de jour
- Nuit :
  - Zombie en majorité fort, les armes a feu produise du bruit qui attire les rapaces
  - Zombie spéciaux 170% de vie, 100% de vitesse en groupe de 2 ou 3 et 30 dans une partie de nuit 
