JEU DES ALLUMETTES – PYTHON / TKINTER
===================================

1. DESCRIPTION
-----------
Ce projet est une implémentation du jeu des allumettes en Python avec une
interface graphique réalisée à l’aide de la bibliothèque Tkinter.

Le programme respecte une architecture MVC (Modèle – Vue – Contrôleur)
et inclut une intelligence artificielle basée sur l’apprentissage par
renforcement (value function).

2. RÈGLES DU JEU
-------------
- Un nombre initial d’allumettes est placé sur la table.
- Deux joueurs jouent à tour de rôle.
- À chaque tour, un joueur peut retirer 1, 2 ou 3 allumettes.
- Le joueur qui prend la dernière allumette perd la partie.

Le jeu peut opposer :
- Un joueur humain
- Une IA aléatoire (RandomAI)
- Une IA apprenante (AI) utilisant une stratégie epsilon-greedy
  et une fonction de valeur apprise par expérience.

3. ARCHITECTURE DU PROJET
----------------------
Le projet est structuré selon le modèle MVC :

- Modèle (model/)
  Gère l’état du jeu, les règles, les joueurs et le nombre d’allumettes.

- Vue (view/)
  Gère l’interface graphique Tkinter (affichage, boutons, messages).

- Contrôleur (controller/)
  Fait le lien entre le modèle et la vue, gère les tours de jeu et la logique
  générale.

4. ARBORESCENCE DU PROJET
----------------------
project/
|
|-- main.py
|-- training.py
|-- alice_training.json (généré après entraînement)
|-- bob_training.json (généré après entraînement)
|-- randy_training.json (généré après entraînement)
|-- README.md
|-- requirements.txt
|
|-- model/
|   |-- game_model.py
|   |-- player.py
|
|-- view/
|   |-- game_view.py
|
|-- controller/
|   |-- game_controller.py

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
Depuis la racine du projet, exécuter :

    python main.py

Une fenêtre graphique s’ouvre et le jeu peut commencer.

9. UTILISATION
-----------
- Le joueur humain joue en cliquant sur les boutons :
  "Prendre 1", "Prendre 2" ou "Prendre 3".
- L’ordinateur joue automatiquement après le tour du joueur humain et un court délai.
- À la fin de la partie :
  - le bouton "Recommencer" permet de lancer une nouvelle partie,
  - le bouton "Terminer" affiche les statistiques finales (victoires, défaites, parties jouées pour chaque joueur) puis ferme l’application

10. SPÉCIFICATIONS ET BONNES PRATIQUES
---------------------------------
- Toutes les classes, méthodes et fonctions sont documentées avec des docstrings.
- Le code est rédigé en anglais.
- Les commentaires peuvent être en français.
- Aucune entrée utilisateur via la console dans la version GUI. 
  La classe Human (console) existe uniquement pour la partie 1.
- Le projet respecte les principes de clean code et de programmation orientée
  objet.
- L’interface graphique est réalisée exclusivement avec Tkinter.

11. ENTRAÎNEMENT DE L’INTELLIGENCE ARTIFICIELLE
---------------------------------------
Le fichier training.py permet :
- D’entraîner les IA sur un grand nombre de parties
- De comparer leurs performances
- D’observer l’évolution de la value function
  La mise à jour de la fonction de valeur suit une règle de type Temporal-Difference :
  V(s) ← V(s) + α [V(s') − V(s)]
- De sauvegarder les paramètres appris dans des fichiers JSON

Lancer l’entraînement :

    python training.py

Deux configurations sont testées :
- 1000 parties
- 100000 parties
Les résultats sont affichés dans la console.

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
