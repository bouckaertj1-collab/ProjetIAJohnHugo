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

QLearningKart utilise un apprentissage par renforcement basé sur une Q-table.

L’objectif de l’IA est d’apprendre à terminer un circuit sans se crasher.
L’entraînement se fait en solo, sans interface graphique :

- un kart Q-learning est placé sur le circuit ;
- il joue un grand nombre de courses automatiquement ;
- il observe un état simplifié du circuit ;
- il choisit une action avec une stratégie epsilon-greedy ;
- il reçoit une récompense après l’action ;
- il met à jour sa Q-table ;
- la Q-table est sauvegardée dans une base SQLite.

Une Q-table est sauvegardée par circuit. Cela permet à l’IA d’apprendre une
stratégie adaptée à chaque tracé.

5.3 Q-table
-----------

La Q-table est représentée en mémoire par un dictionnaire Python :

    {
        state: {
            "accelerate": value,
            "brake": value,
            "turn_left": value,
            "turn_right": value,
            "pass": value,
        }
    }

Un état représente une situation observée par le kart.  
Pour chaque état, l’IA stocke une valeur par action possible.

Une Q-value représente l’intérêt estimé de choisir une action dans un état donné.
Plus la valeur est élevée, plus l’action est considérée intéressante à long terme.

Pendant l’entraînement, l’IA utilise une stratégie epsilon-greedy :

- avec une probabilité epsilon, elle explore une action autorisée au hasard ;
- sinon, elle choisit l’action autorisée avec la meilleure Q-value.

Pendant l’évaluation ou dans le jeu final, epsilon est mis à 0.0 afin que l’IA
n’explore plus et utilise uniquement ce qu’elle a appris.

5.4 État utilisé
----------------

L’état utilisé par QLearningKart est un tuple discret :

    (
        row,
        col,
        front_distance,
        front_terrain,
        left_distance,
        left_terrain,
        right_distance,
        right_terrain,
        direction_index,
        speed,
        current_terrain,
    )

Détail des informations :

- row, col : position actuelle du kart sur le circuit ;
- front_distance : distance discrétisée vers le premier terrain important devant ;
- front_terrain : type du terrain détecté devant ;
- left_distance : distance discrétisée vers le premier terrain important à gauche ;
- left_terrain : type du terrain détecté à gauche ;
- right_distance : distance discrétisée vers le premier terrain important à droite ;
- right_terrain : type du terrain détecté à droite ;
- direction_index : direction actuelle encodée sous forme d’entier ;
- speed : vitesse actuelle du kart ;
- current_terrain : type du terrain sous le kart.

Les types de terrain sont représentés par des constantes nommées dans le code :

- ROAD_CODE
- GRASS_CODE
- FINISH_CODE
- WALL_CODE
- OUT_OF_BOUNDS_CODE

La position est conservée volontairement dans l’état, car l’IA est entraînée
séparément pour chaque circuit. Cela permet d’apprendre une stratégie spécifique
au tracé. L’état contient aussi les types de terrain autour du kart afin que
l’IA ne connaisse pas seulement une distance, mais aussi la nature de ce qu’elle
voit : route, herbe, mur, ligne d’arrivée ou sortie du circuit.

5.5 Actions
-----------

Les actions possibles sont :

- accelerate : augmente la vitesse ;
- brake : diminue la vitesse, jusqu’à permettre la marche arrière ;
- turn_left : change uniquement la direction vers la gauche ;
- turn_right : change uniquement la direction vers la droite ;
- pass : ne change ni la vitesse ni la direction.

Important : pass ne signifie pas forcément que le kart ne bouge pas.
L’action pass conserve simplement la vitesse et la direction actuelles.
Si le kart a déjà une vitesse de 1 ou 2, il continue donc à avancer après
l’action.

Les actions turn_left et turn_right ne ralentissent plus le kart. Le
ralentissement est uniquement lié à l’action brake.

5.6 Actions autorisées pour l’IA
--------------------------------

La liste des actions autorisées est calculée dans Race, car elle dépend des
règles de course et du circuit.

Race filtre notamment :

- les actions qui provoqueraient immédiatement un crash ;
- les actions qui feraient sortir le kart du circuit ;
- les virages à vitesse maximale pour l’IA Q-learning.

Le filtrage des virages à vitesse maximale ne change pas la physique du jeu.
Il sert uniquement à stabiliser l’apprentissage. Après suppression de l’ancien
ralentissement implicite dans turn_left et turn_right, l’IA avait tendance à
apprendre des comportements circulaires sur certains grands circuits. Ce filtre
force donc l’IA à freiner avant certains virages rapides.

5.7 Récompense
--------------

La récompense guide l’apprentissage de l’IA.

Le calcul de récompense utilise principalement :

- une forte pénalité si le kart se crashe ;
- une forte récompense si le kart termine la course ;
- une petite pénalité de temps à chaque action ;
- une récompense intermédiaire lorsqu’un tour est complété ;
- une pénalité lorsque le kart roule sur l’herbe ;
- une pénalité supplémentaire si une action autre que pass ne provoque aucun déplacement.

L’action pass n’est pas punie automatiquement comme une mauvaise action.
Elle peut être optimale si le kart a déjà une bonne vitesse et une bonne
direction.

5.8 Paramètres d’apprentissage
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

5.9 Sauvegarde de la Q-table
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

La Q-table est sauvegardée périodiquement pendant l’entraînement, puis une
dernière fois à la fin.

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
- la Q-table est mise à jour après chaque action ;
- la Q-table est sauvegardée périodiquement ;
- la Q-table finale est sauvegardée à la fin ;
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