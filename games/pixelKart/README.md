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
  Gère la lecture et l’écriture des circuits sauvegardés dans un fichier texte,
  ainsi que la sauvegarde des Q-tables de l’IA Q-learning dans une base SQLite.

4. ARBORESCENCE DU PROJET
-------------------------
games/pixelKart/
|
|-- automated_training.py
|-- circuits.txt
|-- README.md
|
|-- controller/
|   |-- app_controller.py
|   └── race_controller.py
|
|-- dao/
|   |-- circuit_dao.py
|   |-- Q_table_dao.py
|   |-- q_table_service.py
|   └── q_tables.db
|
|-- model/
|   |-- circuit.py
|   |-- dto.py
|   |-- kart.py
|   |-- kart_factory.py
|   └── race.py
|
└── view/
    |-- circuit_editor.py
    |-- circuit_frames.py
    |-- menu_view.py
    └── race_view.py

5. IA
-----
PixelKart contient deux types d’IA :

- RandomAIKart
- QLearningKart

5.1 IA aléatoire
----------------
L’IA aléatoire choisit une action au hasard parmi les actions disponibles :

- accelerate
- brake
- turn_left
- turn_right
- pass

Elle sert principalement à tester le moteur de course et à fournir un adversaire simple.

5.2 IA Q-learning
-----------------
La deuxième IA utilise un apprentissage par renforcement basé sur une Q-function.

Contrairement à d’autres jeux du projet, l’IA de PixelKart n’a pas besoin
de s’entraîner contre un adversaire. Son objectif est simplement de terminer
le circuit le plus efficacement possible sans se crasher.

L’entraînement se fait donc en solo :
- un seul kart Q-learning est placé sur le circuit ;
- il joue des milliers de courses sans interface graphique ;
- il reçoit une récompense après chaque action ;
- il met à jour sa Q-table ;
- la Q-table est ensuite sauvegardée dans une base SQLite.

5.3 Q-table
-----------
La Q-table est représentée en mémoire par un dictionnaire de ce type :

    {
        state: {
            "accelerate": value,
            "brake": value,
            "turn_left": value,
            "turn_right": value,
            "pass": value,
        }
    }

Chaque état est associé à une valeur pour chaque action possible.
Pendant l’entraînement, l’IA utilise une stratégie epsilon-greedy :
elle explore parfois une action aléatoire, puis exploite progressivement
les meilleures actions apprises.

5.4 État utilisé
----------------
Un état correspond à une situation simplifiée du kart sur le circuit.

L’état utilisé est :

    (
        row,
        col,
        front_distance,
        left_distance,
        right_distance,
        direction_index,
        speed,
        terrain_type,
    )

Détail des informations :
- row, col : position du kart sur la grille ;
- front_distance : distance à l’obstacle devant le kart ;
- left_distance : distance à l’obstacle à gauche ;
- right_distance : distance à l’obstacle à droite ;
- direction_index : direction actuelle du kart ;
- speed : vitesse actuelle ;
- terrain_type : type de terrain actuel, route ou herbe.

Le nombre de tours déjà effectués n’est pas inclus dans l’état.
Cela permet d’avoir une Q-table générale par circuit. La stratégie de conduite
reste la même, que la course fasse 1, 2 ou 3 tours.

5.5 Actions
-----------
Les actions possibles sont :

- accelerate : augmente la vitesse ;
- brake : diminue la vitesse, jusqu’à permettre la marche arrière ;
- turn_left : tourne à gauche et ralentit jusqu’à 0 au minimum ;
- turn_right : tourne à droite et ralentit jusqu’à 0 au minimum ;
- pass : ne change pas l’état du kart.

Les virages ralentissent le kart, mais ne peuvent pas le faire passer
en marche arrière. Cela évite un comportement incohérent où plusieurs
virages successifs faisaient reculer le kart.

5.6 Récompense
--------------
La récompense guide l’apprentissage de l’IA.

Les principales récompenses sont :

- +5000 si le kart termine la course ;
- -1000 si le kart percute un mur ;
- +20 lorsqu’il découvre une nouvelle position ;
- +2 lorsqu’il avance ;
- -2 s’il reste sur place ;
- -5 s’il roule sur l’herbe ;
- -1 s’il choisit pass.

Le kart démarre sur la ligne F, qui sert à la fois de départ et d’arrivée.
Pour cette raison, la récompense ne se base pas simplement sur la proximité
avec la ligne d’arrivée. Sinon, l’IA serait encouragée à rester près du départ.
Elle est plutôt récompensée pour explorer le circuit et terminer réellement
un tour complet.

5.7 Paramètres d’apprentissage
------------------------------
Les paramètres principaux sont :

    alpha = 0.2
    gamma = 0.95
    epsilon = 0.95

- alpha contrôle la vitesse d’apprentissage ;
- gamma contrôle l’importance des récompenses futures ;
- epsilon contrôle l’exploration.

Pendant l’entraînement, epsilon diminue progressivement afin que l’IA explore
beaucoup au début, puis exploite davantage sa Q-table.

5.8 Sauvegarde de la Q-table
----------------------------
Les Q-tables sont sauvegardées dans une base SQLite :

    games/pixelKart/dao/q_tables.db

Le projet utilise deux tables principales :

    agents
    q_values

La table agents contient un agent par circuit.
La table q_values contient les valeurs apprises pour chaque état et chaque action.

La structure logique est donc :

    un circuit = un agent = une Q-table

Cela permet d’éviter de mélanger les apprentissages de plusieurs circuits.

6. ENTRAÎNEMENT DE L’IA
-----------------------
L’entraînement de l’IA Q-learning se fait avec le script :

    games/pixelKart/automated_training.py

Depuis la racine du projet, lancer :

    python -m games.pixelKart.automated_training

Le script entraîne automatiquement une IA pour chaque circuit présent dans :

    games/pixelKart/circuits.txt

Pour chaque circuit :
- un kart Q-learning est créé ;
- la Q-table du circuit est chargée si elle existe ;
- l’IA joue un grand nombre de courses sans interface graphique ;
- la Q-table est mise à jour ;
- la Q-table finale est sauvegardée dans q_tables.db ;
- une évaluation est lancée avec epsilon = 0.0.

La version finale utilise une Q-table par circuit, et non une Q-table par
nombre de tours. Cela rend l’apprentissage plus efficace : l’IA apprend
à conduire correctement sur le circuit, puis cette même stratégie peut être
réutilisée pour une course de 1, 2, 3 tours ou plus.

Exemple de résultat obtenu après entraînement :

    Finish: 1000/1000 (100.0%)
    Crash: 0
    Timeout: 0

7. INSTALLATION
---------------
Installer les dépendances avec :

    pip install -r requirements.txt

Remarque :
Tkinter fait partie de la bibliothèque standard Python et ne nécessite pas
d’installation supplémentaire. SQLAlchemy est utilisé pour la base SQLite
qui sauvegarde les Q-tables de l’IA Q-learning.

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
  - le nombre d’IA aléatoires,
  - le nombre d’IA Q-learning,
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