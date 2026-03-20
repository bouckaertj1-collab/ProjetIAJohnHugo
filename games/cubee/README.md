CUBEE – PYTHON / TKINTER
========================

1. DESCRIPTION
-----------
Ce projet est une implémentation du jeu Cubee en Python avec une
interface graphique réalisée à l’aide de la bibliothèque Tkinter.

Le programme respecte une architecture MVC (Modèle – Vue – Contrôleur)
et inclut un joueur contrôlé par un joueur random.

2. RÈGLES DU JEU
-------------
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
- Un joueur humain
- Une IA aléatoire (RandomAgent)

3. ARCHITECTURE DU PROJET
----------------------
Le projet est structuré selon le modèle MVC :

- Modèle
  Gère l’état du jeu, les règles, le plateau, les joueurs et le score.

- Vue
  Gère l’interface graphique Tkinter (affichage, grille, boutons, messages).

- Contrôleur
  Fait le lien entre le modèle et la vue, gère les actions du joueur
  et la logique générale.

4. ARBORESCENCE DU PROJET
----------------------
cubee/
|
|-- game_controller.py
|-- game_model.py
|-- game_view.py
|-- player.py
|-- README.md
|
└── tests/
    └── test_game_model.py

5. PRÉREQUIS
---------
- Python >= 3.10
- Tkinter (inclus par défaut avec Python)

6. ENVIRONNEMENT VIRTUEL (RECOMMANDÉ)
---------------------------------
Création de l’environnement virtuel :

    python -m venv env

Activation :

Windows :
    env\Scripts\activate

Linux / macOS :
    source env/bin/activate

7. INSTALLATION DES DÉPENDANCES
----------------------------
Installer les dépendances avec :

    pip install -r requirements.txt

Remarque :
Tkinter fait partie de la bibliothèque standard Python et ne nécessite pas
d’installation supplémentaire.

8. LANCEMENT DU PROGRAMME
----------------------
Le jeu Cubee se lance depuis le launcher principal du projet.

Depuis la racine du projet, exécuter :

    python main.py

Ensuite, sélectionner **Cubee** dans la fenêtre du launcher.

9. UTILISATION
-----------
- Le joueur humain joue en cliquant sur une case adjacente à sa position.
- Le contrôleur convertit ce clic en déplacement valide.
- L’ordinateur joue automatiquement lorsque c’est le tour de l’IA.
- À la fin de la partie :
  - un message annonce le gagnant ou l’égalité,
  - le bouton "Reset" permet de relancer une nouvelle partie,
  - le bouton "Quit" ferme la fenêtre du jeu.

10. SPÉCIFICATIONS ET BONNES PRATIQUES
---------------------------------
- Toutes les classes, méthodes et fonctions sont documentées avec des docstrings.
- Le code est rédigé en anglais.
- Les commentaires peuvent être en français.
- Le projet respecte les principes de clean code et de programmation orientée
  objet.
- L’interface graphique est réalisée exclusivement avec Tkinter.
- Le jeu est intégré au launcher principal du projet.

11. TESTS
-------
Les tests de Cubee vérifient principalement la logique du modèle de jeu.

Lancer les tests de Cubee :

    pytest games/cubee/tests

Ou lancer tous les tests du projet :

    pytest

12. AUTEURS
-------
Projet réalisé par :
Bouckaert John / Hugo Fievet

Cadre :
Projet pédagogique – Python / Tkinter
Année : 2025–2026

13. LICENSE
-------
This project is licensed under the MIT License.