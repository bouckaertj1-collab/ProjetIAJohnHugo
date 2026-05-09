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
│   └── PixelKart/
│       ├── dao/                  # Accès à la base de données (Q-tables, circuits)
│       │   ├── Q_table_dao.py    # Gestion des Q-tables en SQLite
│       │   └── q_table_service.py
│       ├── model/                # Logique métier
│       │   ├── kart.py           # Classes Kart, QLearningKart, etc.
│       │   ├── circuit.py        # Gestion des circuits
│       │   ├── race.py           # Logique des courses
│       │   └── kart_factory.py   # Factory pour créer des karts
│       ├── view/                 # Interface utilisateur (Tkinter)
│       │   ├── race_view.py      # Affichage de la course
│       │   └── menu_view.py      # Menu principal
│       └── controller/           # Contrôleurs
│           ├── race_controller.py
│           └── app_controller.py
├── launcher/                     # Point d'entrée du jeu
├── circuits.txt                  # Liste des circuits personnalisés
├── requirements.txt              # Dépendances Python
└── README.md                     # Documentation

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

## ⚠️ Problèmes connus

- Les karts Q-Learning peuvent parfois tourner en rond sur des circuits complexes.
- La détection de la ligne d'arrivée peut être sensible à la direction du kart.
- Les performances dépendent fortement des hyperparamètres (`epsilon`, `alpha`, `gamma`).

6. ✨ Fonctionnalités
------------

- **Création de circuits** : Éditeur intégré pour concevoir des circuits personnalisés (murs, herbe, ligne d'arrivée).
- **Types de karts** :
  - **Humain** : Contrôlé via l'interface graphique.
  - **IA aléatoire** : Prend des décisions aléatoires.
  - **IA Q-Learning** : Apprend à optimiser ses trajectoires via l'apprentissage par renforcement.
- **Entraînement automatique** : Script pour entraîner un kart Q-Learning sur N courses et sauvegarder sa Q-table.
- **Sauvegarde des progrès** : Persistance des Q-tables en base de données SQLite.
- **Métriques de suivi** : Affichage des récompenses, du nombre d'états explorés, et des tours complétés.


7. PRÉREQUIS
------------
- Python >= 3.10
- Tkinter (inclus par défaut avec Python)
- sqlalchemy>=2.0.0
- matplotlib>=3.7.0
- numpy>=1.24.0

8. INSTALLATION
---------------
Installer les dépendances avec :

    pip install -r requirements.txt

Remarque :
Tkinter fait partie de la bibliothèque standard Python et ne nécessite pas
d’installation supplémentaire.

9. LANCEMENT DU PROGRAMME
-------------------------

9.1 Lancer le projet
--------------------
Le jeu PixelKart se lance depuis le launcher principal du projet.

Depuis la racine du projet, exécuter :

    python main.py

Ensuite, sélectionner **PixelKart** dans la fenêtre du launcher.

9.2 Fenêtres du jeu
-------------------
Le launcher ouvre PixelKart dans une fenêtre dédiée.

Le jeu propose :
- un menu de configuration,
- un éditeur de circuits,
- une fenêtre de course.

10. UTILISATION
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

11. SAUVEGARDE DES CIRCUITS
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