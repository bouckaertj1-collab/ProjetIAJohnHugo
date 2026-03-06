import random


class RandomAgent:
    """
    IA très simple qui choisit un coup aléatoire parmi les coups possibles.
    """

    def __init__(self, player_id):
        self.player_id = player_id

    def choose_action(self, model):
        if model.player_turn != self.player_id:
            return None

        moves = model.available_moves()

        if not moves:
            return None

        return random.choice(moves)