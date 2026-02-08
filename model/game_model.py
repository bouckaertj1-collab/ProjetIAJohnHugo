# model/game_model.py
import random

class GameModel:
    """
    Modèle du jeu des allumettes (logique + état).
    Règle: le joueur qui prend la dernière allumette perd.
    """

    def __init__(self, total_matches, player1, player2, displayable=True):
        self.nb = total_matches
        self.original_nb = total_matches
        self.displayable = displayable

        self.player1 = player1
        self.player2 = player2

        # on "attache" la partie aux joueurs
        self.player1.game = self
        self.player2.game = self

        # 0 => player1, 1 => player2 (comme dans l'énoncé)
        self.current_player = 0

        self._is_over = False
        self._winner = None
        self._loser = None

        self.shuffle()

    def shuffle(self):
        """Mélange les joueurs et choisit qui commence."""
        players = [self.player1, self.player2]
        random.shuffle(players)
        self.player1, self.player2 = players[0], players[1]

        # IMPORTANT: le tour repart sur player1 après mélange
        self.current_player = 0

    def reset(self):
        """Remet la partie à 0 et mélange les joueurs."""
        self.nb = self.original_nb
        self._is_over = False
        self._winner = None
        self._loser = None
        self.shuffle()

    def display(self):
        """Affiche l'état du jeu en console si displayable=True."""
        if self.displayable:
            print(f"Allumettes restantes: {self.nb}")

    def switch_player(self):
        """Change le joueur actuel."""
        self.current_player = 1 - self.current_player

    def is_game_over(self):
        return self._is_over

    def get_current_player(self):
        return self.player1 if self.current_player == 0 else self.player2

    def get_winner(self):
        return self._winner

    def get_loser(self):
        return self._loser

    def step(self, action):
        """
        Applique un coup: retirer 1, 2 ou 3 allumettes.
        NOTE: ne change PAS de joueur ici (le contrôleur le fait).
        """
        if self._is_over:
            raise ValueError("Partie déjà terminée.")

        if action not in (1, 2, 3):
            raise ValueError("Action invalide: il faut 1, 2 ou 3.")

        if action > self.nb:
            raise ValueError("Action invalide: pas assez d'allumettes restantes.")

        # applique le coup
        self.nb -= action

        # fin de partie: celui qui a joué perd si nb == 0
        if self.nb == 0:
            self._is_over = True
            self._loser = self.get_current_player()
            # gagnant = l'autre joueur
            other = self.player2 if self.current_player == 0 else self.player1
            self._winner = other
