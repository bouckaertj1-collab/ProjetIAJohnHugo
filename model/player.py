import random

class Player:
    """
    Joueur générique (random par défaut).
    """

    def __init__(self, name, game=None):
        self.name = name
        self.game = game
        self.nb_wins = 0
        self.nb_loses = 0

    @property
    def nb_games(self):
        return self.nb_wins + self.nb_loses

    @staticmethod
    def play():
        """
        Choisit aléatoirement un nombre entre 1 et 3.
        (Comportement par défaut demandé)
        """
        return random.randint(1, 3)

    def win(self):
        self.nb_wins += 1

    def lose(self):
        self.nb_loses += 1

    def __str__(self):
        return f"{self.name} (W:{self.nb_wins} L:{self.nb_loses} G:{self.nb_games})"
