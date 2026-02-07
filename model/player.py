# player.py
import random

class Player:
    """
    Classe représentant un joueur générique.
    Elle sera héritée par Human et AI.
    """

    def __init__(self, name, game=None):
        # Nom du joueur
        self.name = name

        # Référence vers la partie en cours
        self.game = game

        # Statistiques
        self.nb_wins = 0
        self.nb_loses = 0

    @property
    def nb_games(self):
        """
        Nombre total de parties jouées
        """
        return self.nb_wins + self.nb_loses

    @staticmethod
    def play():
        """
        Comportement par défaut :
        choisir aléatoirement entre 1 et 3 allumettes.
        """
        return random.randint(1, 3)

    def win(self):
        """
        Appelée quand le joueur gagne
        """
        self.nb_wins += 1

    def lose(self):
        """
        Appelée quand le joueur perd
        """
        self.nb_loses += 1

    def __str__(self):
        return (
            f"{self.name} | "
            f"Victoires: {self.nb_wins}, "
            f"Défaites: {self.nb_loses}, "
            f"Parties: {self.nb_games}"
        )
