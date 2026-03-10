import random


class Player:
    """
    Représente un joueur de Cubee.
    """

    def __init__(self, name, position, color=None):
        self.name = name
        self.position = position
        self.color = color

        self.nb_win = 0
        self.nb_lose = 0
        self.nb_draw = 0
        self.nb_game = 0

    def is_ai(self):
        return False

    def play(self, game_model):
        """Retourne le coup à jouer."""
        return None

    def win(self):
        self.nb_win += 1
        self.nb_game += 1

    def lose(self):
        self.nb_lose += 1
        self.nb_game += 1

    def draw(self):
        self.nb_draw += 1
        self.nb_game += 1

    def __repr__(self):
        return f"Player(name={self.name}, position={self.position})"

class RandomAgent(Player):
    """
    IA très simple qui joue un coup aléatoire.
    """

    def is_ai(self):
        return True

    def play(self, game_model):
        if game_model.get_current_player() != self:
            return None

        moves = game_model.available_moves(self)
        if not moves:
            return None

        return random.choice(moves)