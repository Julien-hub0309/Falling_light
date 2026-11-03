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

## arbre des classe
### assaut
- starter assaut
	- general assaut 
		- reinforce general assaut 
			- expert general assaut
	
	- specialised assault 
		- reinforce specialised assaut 
			- expert specialised assaut
	
	- assaut recon 
		- reinforce assaut recon 
			- expert assaut recon
	
	- position holding
		- counter fire 
			- expert counter fire
"## tactic
- starter tactic
	- light gunner 
		- reinforce light gunner
			- expert light gunner
	
	- runner 
		- reinforce runner
			- expert runner
	
	- quick intervention 
		- reinforce quick intervention
			- expert quick intervention
	
	- melee tactician 
		- melee master 
			- expert melee master
### precision (sniper)
- starter precision
	- sharpshooter
		- reinforce sharpshooter
			- expert sharpshooter
	
	- railgunner 
		- reinforce railgunner
			- expert railgunner
	
	- flawless 
		- reinforce flawless
			- expert flawless
	
	- hidden sniper 
		- grip sniper 
			- expert grip sniper
### breech
- starter breech
	- heavy assault
		- high caliber 
			- expert high caliber
	
	- shotgunner 
		- reinforce shotgunner
			- expert shotgunner
	
	- war danger 
		- heavy war danger
			- expert war danger
	
	- wall destroyer 
		- building demolisher 
			- expert building demolisher
	
	- bazooka holder
		- expert bazooka holder
			- explosive weapon master 
### silent
- starter silent
	- agent
		- spy 
			- spy master
	
	- sound maker 
		- sound breaker
			- expert sound breaker
	
	- sound searcher 
		- expert sound searcher
			- xray searcher
	
	- ninja
		- ninja expert
			- ninja master
### support
- starter support
	- recon
		- recon commander 
			- expert recon commander
	
	- engineer
		- weapon engineer 
			- expert war engineer
	
	- medic
		- battle medic 
			- expert medic field
	
	- protector
		- heavy shield 
			- expert heavy shield
	
	- builder
		- war constructor 
			- expert war constructor
### polyvalent
- starter polyvalent
	- soldier
		- heavy soldier 
			- heavy commander
		
		- light soldier 
			- light commander
	
	- pilot 
		- expert pilot
			- pilot commander
	
	- weapon specialist 
		- weapon expert
			- weapon researcher
	
	- arms trafficker 
		- weapon cartel commander
			- chief weapon dealeur
