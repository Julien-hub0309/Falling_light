# Falling_light

## Idée amélioration : 

### Multi-joueur local : 

- server.py -> créer un serveur temporaire lie les pc en jeux et leur permet de jouer entre eux
  - server_client -> écoutes et envoie les paramètres a server de jeux
  - server_game.py -> le serveurs qui lie les pc entre eux a lancer pas le gamemaster
 

### Craft : 
- le loot rouge :
  - permetttra après 3 récupération d'augmenter les dégats des armes de corps a corps 
  - permettra après 5 récupération d'avoir l'armes a feu de sa classe
  - permettra après 10 récupération permet d'avoir une amélioration de l'arme a feu 
- le loot ourange permet le craft de grenade lier a la classe ou munition
- le loot bleu c'est pour craft des kit de d'armure utilisable avec une touche
- le loot vert c'est pour craft des kit de soins utilisable avec une touche

### Armes et classe : 
- Choisir la classe au début pour les compétences de départ et armes disponible
- Ouverture de la game avec que le couteau en arme de corps a corps

### Zombie normal + spéciaux : 
- Jour :
  - Zombie en majorité faible, les armes a feu produise du bruit qui attire les zombie spéciaux
  - Zombie normal 150% de vie 80% de vitesse en groupe de 3 ou 4 pour 40 zombie dans une partie de jour
- Nuit :
  - Zombie en majorité fort, les armes a feu produise du bruit qui attire les rapaces
  - Zombie spéciaux 170% de vie, 100% de vitesse en groupe de 2 ou 3 et 30 dans une partie de nuit 
