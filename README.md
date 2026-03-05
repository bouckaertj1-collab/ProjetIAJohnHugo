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
Actuellement, les jeux suivants sont disponibles :

- Matchsticks (jeu des allumettes)
- Cubee (à venir)
- PixelKart (à venir)

Chaque jeu est isolé dans son propre dossier afin de garder une
architecture claire et modulaire.

3. ARCHITECTURE DU PROJET
----------------------
Le projet est structuré selon une architecture modulaire :

- Controller (controller/)
  Gère la logique globale de l’application et le menu principal.

- View (view/)
  Contient l’interface graphique du launcher (menu principal).

- Games (games/)
  Contient les différents jeux implémentés dans l’application.
  Chaque jeu possède sa propre architecture MVC.

4. ARBORESCENCE DU PROJET
----------------------
ProjetIAJohnHugo/
│
├── main.py
├── README.md
├── requirements.txt
│
├── launcher/
│   ├── controller.py
│   └── view.py
│
└── games/
    ├── matchsticks/
    │   ├── controller/
    │   ├── model/
    │   ├── view/
    │   ├── training.py
    │   └── README.md
    │
    ├── cubee/
    └── pixel_kart/

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

Une fenêtre graphique s’ouvre affichant le menu principal permettant
de sélectionner un jeu.

9. UTILISATION
-----------
- L’utilisateur sélectionne le jeu souhaité dans le menu principal.
- Une nouvelle fenêtre s’ouvre contenant l’interface du jeu choisi.
- Chaque jeu possède ses propres règles et son propre fonctionnement.

10. SPÉCIFICATIONS ET BONNES PRATIQUES
---------------------------------
- Le projet respecte une architecture MVC.
- Chaque jeu est isolé dans un dossier indépendant.
- Toutes les classes, méthodes et fonctions sont documentées avec des docstrings.
- Le code est rédigé en anglais.
- L’interface graphique est réalisée exclusivement avec Tkinter.

11. AUTEURS
-------
Projet réalisé par :
Bouckaert John / Hugo Fievet

Cadre :
Projet pédagogique – Python / Tkinter
Année : 2025–2026

12. LICENSE
-------
This project is licensed under the MIT License.