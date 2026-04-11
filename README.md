PROJET IA – PYTHON / TKINTER
============================

1. DESCRIPTION
-----------
Ce projet est une application Python contenant plusieurs jeux implémentés
avec une interface graphique réalisée à l’aide de la bibliothèque Tkinter.

L’application utilise une architecture MVC (Modèle – Vue – Contrôleur)
et un menu principal permettant de sélectionner le jeu à lancer.

Chaque jeu possède sa propre implémentation MVC et peut inclure une
intelligence artificielle basée sur l’apprentissage par renforcement.

2. JEUX DISPONIBLES
----------------
Les jeux suivants sont disponibles :

- Matchsticks
- Cubee 
- PixelKart 

Chaque jeu est isolé dans son propre dossier afin de garder une
structure claire.

3. ARCHITECTURE DU PROJET
----------------------
Le projet est structuré selon une architecture modulaire :

- Controller 
  Gère la logique globale de l’application et le menu principal.

- View 
  Contient l’interface graphique du launcher (menu principal).

- Games 
  Contient les différents jeux implémentés dans l’application.
  Chaque jeu possède sa propre architecture MVC.

4. ARBORESCENCE DU PROJET
----------------------
ProjetIAJohnHugo/
├── README.md
├── requirements.txt
├── main.py
├── launcher/
│   ├── controller.py
│   └── view.py
├── games/
│   ├── cubee/
│   │   ├── README.md
│   │   ├── game_controller.py
│   │   ├── game_model.py
│   │   ├── game_view.py
│   │   ├── player.py
│   │   ├── qtable_dao.py
│   │   ├── trainer.py
│   │   ├── training_results/
│   │   └── tests/
│   │       └── test_game_model.py
│   ├── matchsticks/
│   │   ├── README.md
│   │   ├── game_controller.py
│   │   ├── game_model.py
│   │   ├── game_view.py
│   │   ├── player.py
│   │   ├── training.py
│   │   ├── alice_training.json
│   │   ├── bob_training.json
│   │   └── randy_training.json
│   └── pixelKart/
│       ├── README.md
│       ├── controller/
│       └── circuits.txt
│       │   ├── game_controller.py
│       │   ├── menu_controller.py
│       │   └── race_controller.py
│       ├── dao/
│       │   └── circuit_dao.py
│       ├── model/
│       │   ├── circuit.py
│       │   ├── dto.py
│       │   ├── kart.py
│       │   └── race.py
│       ├── view/
│       │   ├── circuit_editor.py
│       │   ├── circuit_frames.py
│       │   ├── menu_view.py
│       │   └── race_view.py

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
Le fichier `requirements.txt` contient actuellement `pytest`, utilisé pour lancer les tests

8. LANCEMENT DU PROGRAMME
----------------------
Depuis la racine du projet, exécuter :

    python main.py

Une fenêtre graphique s’ouvre affichant le menu principal permettant
de sélectionner un jeu.

9. LANCEMENT DES TESTS
--------------------
Pour lancer les tests, executer :

    pytest

Ou seulement pour Cubee :

    pytest games/cubee/tests

10. UTILISATION
-----------
- L’utilisateur démarre l’application depuis le launcher principal.
- L’utilisateur sélectionne le jeu souhaité dans le menu principal.
- Une nouvelle fenêtre s’ouvre contenant l’interface du jeu choisi.
- Chaque jeu possède ses propres règles et son propre fonctionnement.
- PixelKart propose en plus un éditeur de circuits permettant de créer,
  modifier et sauvegarder des circuits personnalisés.

11. SPÉCIFICATIONS ET BONNES PRATIQUES
---------------------------------
- Le projet respecte une architecture MVC.
- Chaque jeu est isolé dans un dossier indépendant.
- Toutes les classes, méthodes et fonctions sont documentées avec des docstrings.
- Le code est rédigé en anglais.
- L’interface graphique est réalisée exclusivement avec Tkinter.
- PixelKart utilise également un **DAO** pour la persistance des circuits.

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