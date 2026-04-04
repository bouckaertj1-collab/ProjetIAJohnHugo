CUBEE – PYTHON / TKINTER
========================

1. DESCRIPTION
--------------
Ce projet est une implémentation du jeu **Cubee** en Python avec une
interface graphique réalisée à l’aide de la bibliothèque **Tkinter**.

Le programme respecte une architecture **MVC** (Modèle – Vue – Contrôleur)
et inclut une IA basée sur le **Q-learning**.

Le projet permet :
- de jouer à Cubee contre une IA,
- d’entraîner cette IA automatiquement,
- puis de rejouer contre l’IA entraînée.

2. RÈGLES DU JEU
----------------
- Le jeu se déroule sur une grille carrée.
- Chaque joueur commence dans un coin opposé du plateau.
- À chaque tour, un joueur peut se déplacer d’une case :
  haut, bas, gauche ou droite.
- Un joueur peut se déplacer vers :
  - une case vide,
  - une case qu’il possède déjà.
- Un joueur ne peut pas se déplacer :
  - en dehors du plateau,
  - sur une case appartenant à l’adversaire.
- Après un déplacement, certaines zones fermées peuvent être capturées.
- La partie se termine lorsque le plateau est entièrement rempli.
- Le gagnant est le joueur qui possède le plus de cases à la fin.

Le jeu peut opposer :
- un joueur humain
- une IA apprenante

3. ARCHITECTURE DU PROJET
-------------------------
Le projet est structuré selon le modèle MVC :

- **Modèle**  
  Gère l’état du jeu, les règles, le plateau, les joueurs et le score.

- **Vue**  
  Gère l’interface graphique Tkinter (affichage, grille, boutons, messages).

- **Contrôleur**  
  Fait le lien entre le modèle et la vue, gère les actions du joueur
  et le déroulement de la partie.

4. ARBORESCENCE DU PROJET
-------------------------
games/cubee/
|
|-- game_controller.py
|-- game_model.py
|-- game_view.py
|-- player.py
|-- qtable_dao.py
|-- trainer.py
|-- cubee_trained_qtable.json
|-- training_results/
|   |-- training_summary.json
|   └── qtables/
|-- README.md
|
└── tests/
    └── test_game_model.py

5. IA
-----
L’IA repose sur une **Q-table** qui associe une valeur à chaque couple
**(état, action)**.

L’état prend en compte :
- le tour courant,
- la position de l’IA,
- la position de l’adversaire,
- l’état du plateau.

Les actions possibles sont :
- `up`
- `down`
- `left`
- `right`

L’IA apprend pendant la partie en mettant à jour sa Q-table lorsqu’elle
retrouve la main, donc après la réponse adverse.

La récompense prend en compte :
- le gain de score de l’IA,
- le gain de score de l’adversaire,
- un bonus ou un malus terminal en fin de partie.

Le projet contient aussi un script `trainer.py` permettant :
- d’entraîner l’IA contre un agent aléatoire sur un petit plateau,
- de comparer plusieurs couples de paramètres `(alpha, gamma)`,
- puis de lancer un entraînement intensif en self-play sur un plateau 5x5.

La Q-table finale du self-play est sauvegardée dans :

    games/cubee/cubee_trained_qtable.json

Ce fichier n’est pas inclus dans le dépôt Git, car sa taille devient trop
importante après l’entraînement intensif. Il faut donc d’abord le générer en
lançant le script `trainer.py` via :

    python -m games.cubee.trainer

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

Remarque :
Pour jouer contre l’IA finale entraînée, il faut d’abord lancer :

    python -m games.cubee.trainer

afin de générer le fichier :

    games/cubee/cubee_trained_qtable.json

Une fois ce fichier généré, le launcher peut charger automatiquement l’IA
entraînée.

8.1 Jouer à Cubee
------------------
Le jeu Cubee se lance depuis le launcher principal du projet.

Depuis la racine du projet, exécuter :

    python main.py

Ensuite, sélectionner **Cubee** dans la fenêtre du launcher.

8.2 Lancer l’entraînement
--------------------------
L’entraînement intensif de l’IA se lance sans interface graphique avec :

    python -m games.cubee.trainer

Le script :
- entraîne plusieurs IA contre un agent aléatoire sur petit plateau,
- évalue différents couples `(alpha, gamma)`,
- sélectionne les meilleurs paramètres,
- puis lance un self-play sur un plateau 5x5.

Les résultats sont enregistrés dans :

    games/cubee/training_results/


9. UTILISATION
--------------
- Le joueur humain joue en cliquant sur une case adjacente à sa position.
- Le contrôleur convertit ce clic en déplacement valide.
- L’ordinateur joue automatiquement lorsque c’est le tour de l’IA.
- À la fin de la partie :
  - un message annonce le gagnant ou l’égalité,
  - le bouton "Reset" permet de relancer une nouvelle partie,
  - le bouton "Quit" ferme la fenêtre du jeu.

Pour jouer contre une IA déjà entraînée, le launcher charge la Q-table
sauvegardée dans :

    games/cubee/cubee_trained_qtable.json

Comme ce fichier n’est pas versionné dans le dépôt, il est nécessaire de
lancer d’abord `trainer.py` pour le générer.

10. ENTRAÎNEMENT
----------------
L’entraînement se déroule en deux phases :

10.1 Recherche de paramètres
------------------------------
Plusieurs couples `(alpha, gamma)` sont testés sur un petit plateau
contre un agent aléatoire.

Pour chaque couple :
- l’IA est entraînée sur un certain nombre de parties ;
- puis elle est évaluée sans apprentissage sur une nouvelle série de parties.

Cette phase permet de choisir les paramètres les plus efficaces avant de
passer à un plateau plus grand.

10.2 Self-play final
----------------------
Une fois les meilleurs paramètres trouvés, deux IA s’affrontent sur un
plateau **5x5**.

Les deux agents apprennent en même temps et partagent une même Q-table.
La Q-table finale obtenue est sauvegardée dans :

    games/cubee/cubee_trained_qtable.json

11. TESTS
---------
Les tests de Cubee vérifient principalement la logique du modèle de jeu.

Lancer les tests de Cubee :

    pytest games/cubee/tests

Ou lancer tous les tests du projet :

    pytest

12. AUTEURS
-----------
Projet réalisé par :
Bouckaert John / Hugo Fievet

Cadre :
Projet pédagogique – Python / Tkinter
Année : 2025–2026

13. LICENSE
-----------
This project is licensed under the MIT License.