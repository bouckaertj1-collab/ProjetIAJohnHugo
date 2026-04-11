PIXELKART – PYTHON / TKINTER
===========================

1. DESCRIPTION
--------------
Ce projet est une implémentation du jeu **PixelKart** en Python avec une
interface graphique réalisée à l’aide de la bibliothèque **Tkinter**.

Le programme respecte une architecture **MVC** (Modèle – Vue – Contrôleur)
et inclut un système de persistance des circuits via un **DAO**.

Le projet permet :
- de créer et sauvegarder des circuits,
- de sélectionner un circuit depuis un menu,
- de lancer une course avec joueurs humains et IA,
- d’afficher la course dans une interface graphique dédiée.

2. RÈGLES DU JEU
----------------
- Le jeu se déroule sur un circuit représenté par une grille.
- Les types de cases sont :
  - `R` : route
  - `G` : herbe
  - `W` : mur
  - `F` : ligne de départ / arrivée
- Les karts démarrent sur des cases de la ligne `F`.
- À chaque tour, un kart peut :
  - `accelerate`
  - `brake`
  - `turn_left`
  - `turn_right`
  - `pass`
- Après l’action, le kart se déplace automatiquement selon :
  - sa vitesse
  - sa direction
- Si un kart sort du circuit :
  - sa vitesse est remise à 0
- Si un kart percute un mur :
  - il est éliminé
- Si un kart tente d’entrer sur une case occupée :
  - il s’arrête
- L’herbe ralentit le déplacement :
  - la vitesse effective est divisée par 2, arrondie à l’entier inférieur
- La course se termine lorsqu’un kart vivant atteint le nombre de tours demandé.

3. ARCHITECTURE DU PROJET
-------------------------
Le projet est structuré selon le modèle MVC :

- Modèle 
  Gère les règles du jeu, le circuit, les karts, le déplacement,
  les collisions, les tours et l’état global de la course.

- Vue 
  Gère l’interface Tkinter : menu, écran de course, éditeur de circuit,
  affichage de la grille et des informations des joueurs.

- Contrôleur 
  Fait le lien entre le modèle et la vue, gère les actions de l’utilisateur,
  la navigation entre les écrans et le déroulement de la course.

- DAO
  Gère la lecture et l’écriture des circuits sauvegardés dans un fichier texte.

4. ARBORESCENCE DU PROJET
-------------------------
games/pixelKart/
|
|-- controller/
|   |-- app_controller.py
|   └── race_controller.py
|
|-- dao/
|   └── circuit_dao.py
|
|-- model/
|   |-- circuit.py
|   |-- dto.py
|   |-- kart.py
|   └── race.py
|
|-- view/
|   |-- circuit_editor.py
|   |-- circuit_frames.py
|   |-- menu_view.py
|   └── race_view.py
|
|-- circuits.txt
└── README.md

5. IA
-----
Le projet contient une IA simple de type aléatoire.

Cette IA :
- hérite de la classe Kart,
- choisit aléatoirement une action parmi :
  - accelerate
  - brake
  - turn_left
  - turn_right
  - pass

L’objectif principal de cette IA est de permettre :
- de tester le moteur de jeu,
- de jouer contre des adversaires automatiques,
- et de respecter la structure demandée avec humains + IA.

6. PRÉREQUIS
------------
- Python >= 3.10
- Tkinter (inclus par défaut avec Python)

7. INSTALLATION
---------------
Installer les dépendances avec :

    pip install -r requirements.txt

Remarque :
Tkinter fait partie de la bibliothèque standard Python et ne nécessite pas
d’installation supplémentaire.

8. LANCEMENT DU PROGRAMME
-------------------------

8.1 Lancer le projet
--------------------
Le jeu PixelKart se lance depuis le launcher principal du projet.

Depuis la racine du projet, exécuter :

    python main.py

Ensuite, sélectionner **PixelKart** dans la fenêtre du launcher.

8.2 Fenêtres du jeu
-------------------
Le launcher ouvre PixelKart dans une fenêtre dédiée.

Le jeu propose :
- un menu de configuration,
- un éditeur de circuits,
- une fenêtre de course.

9. UTILISATION
--------------
- Dans le menu, choisir :
  - le nombre de joueurs humains,
  - le nombre d’IA,
  - le nombre de tours,
  - le circuit à utiliser.
- Le bouton Open circuit editor permet :
  - de créer un circuit,
  - de modifier sa taille,
  - de changer les types de cases,
  - de sauvegarder le circuit.
- Le bouton Play lance la course.
- Pendant la course :
  - les joueurs humains utilisent les boutons d’action,
  - les IA jouent automatiquement lorsque c’est leur tour.
- L’écran de course affiche :
  - le circuit,
  - la position des karts,
  - leur direction,
  - leur vitesse,
  - leurs tours effectués,
  - l’état global de la course.
- Le bouton **Back to menu** permet de revenir à l’écran de configuration.

10. SAUVEGARDE DES CIRCUITS
---------------------------
Les circuits sont stockés dans le fichier :

    games/pixelKart/circuits.txt

Chaque circuit est enregistré sous forme :
- d’un nom
- et d’une grille sérialisée

Exemple :

    Basic:GGGG,GRFG,GRRG

Le DAO permet :
- de lire tous les circuits,
- de récupérer un circuit par son nom,
- d’enregistrer un nouveau circuit,
- de mettre à jour l’ensemble du fichier.

11. AUTEURS
-----------
Projet réalisé par :
Bouckaert John / Hugo Fievet

Cadre :
Projet pédagogique – Python / Tkinter
Année : 2025–2026

12. LICENSE
-----------
This project is licensed under the MIT License.