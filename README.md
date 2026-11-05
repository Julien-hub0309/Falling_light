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
  - Zombie géant 220% de vie, 80% de vitesse, 5 dans une partie
 
### Pilot et titan : 
- Conservation de la vitesse du pilot ( course + glissade )
- Donner des ordres simple au titan quand pas embarquée
- Corps a corps titan epee a la place de couteau 

### Mode de jeu : 
- Parcoups : 0 armes, que le couteau et on dois passer par des points sur l amap dans un temps impartie avec les zombie qui nous fonce dessus
- Point de contrôle : rester a un point précis sur la map pendant un temps donner ( 30 seconde ) pour 10 point + tuer des zombie pour 1 point 

### arbre de craft des classes

1. L'Assaut (Frontline / Run & Gun)
Le spécialiste du combat rapproché à moyen terme, pensé pour être constamment en mouvement et au contact.

- Niveau 1 (Passif) - Sprint Amélioré : Vitesse de déplacement augmentée et rechargement plus rapide après un kill.

- Niveau 2 (Actif) - Grappin : Un grappin qui s'accorche a toute les structure.

- Niveau 3 (Ultime) - Surchauffe : Augmente temporairement la cadence de tir, réduit le recul et régénère de la santé à chaque élimination.

2. Le Breacher (Lourd / Démolition)
Le rouleau compresseur conçu pour briser les lignes ennemies, percer les murs et contrôler les espaces.

- Niveau 1 (Passif) - Armure Lourde : Réduction des dégâts explosifs subis et capacité à porter des armes lourdes sans pénalité de vitesse.

- Niveau 2 (Actif) - Charge Explosive : Pose ou tire un projectile qui détruit instantanément les structures et sonne les ennemis à proximité.

- Niveau 3 (Ultime) - Lance-Roquettes : Équipe une arme dévastatrice temporaire pour raser un point stratégique.

3. Le Recon (Précision / Infiltration)
Fusil de précision ou silencieux, il combine les branches « Precision » et « Silent » pour traquer et éliminer proprement.

- Niveau 1 (Passif) - Silencieux & Détection : Vos tirs n'apparaissent pas sur la mini-carte. Détecte les pièges ennemis à travers les murs.

- Niveau 2 (Actif) - Scan Radar : Lance une impulsion sonar pour révéler temporairement la position des ennemis dans un rayon défini.

- Niveau 3 (Ultime) - Camouflage  : Devient quasiment invisible pendant quelques secondes.

4. Le tactique (Soutien & Tactique)
Indispensable pour maintenir l'équipe en vie et ravitailler le front.

- Niveau 1 (Passif) - Sacoche d'armure/Soins : Déploie au sol des packs de soin ou de l'armure pour vous et vos alliés.

- Niveau 2 (Actif) -  Bouclier Portatif : Pose une couverture déployable aborbant les dégâts.

- Niveau 3 (Ultime) - Ranimation / Stym Pack : Possibilité de revenir dans la partie ou de refaire venir un de c'est allié.
