# model/game_model.py
from random import sample

class GameModel:
    """
    Modèle du jeu des allumettes (logique + état).
    Règle: 
        - Le joueur qui prend la dernière allumette perd.
        - Le joueur doit prendre 1 allumette minimum et 3 maximum par tour
    """

    def __init__(self, total_matches, player1, player2, displayable=True):
        self.nb = total_matches
        self.original_nb = total_matches
        self.displayable = displayable

        self.player1 = player1
        self.player2 = player2

        self.player1.game = self
        self.player2.game = self

        self.current_player = None

        self._is_over = False
        self._winner = None
        self._loser = None

        self.shuffle()

    def shuffle(self):
        """Mélange les joueurs"""
        self.player1, self.player2 = sample([self.player1, self.player2],2)
        self.current_player = self.player1

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

        if self.nb == 0:
            self._is_over = True
            self._loser = self.current_player
            self._winner = self.player2 if self._loser == self.player1 else self.player1

    def play(self):
        """
        Joue une partie complète (utile pour tests / IA / console).
        """
        self.reset()

        while not self.is_over:
            self.display()

            action = self.current_player.play()

            
            if action is None:
                raise RuntimeError(
                    "Human.play() a retourné None. "
                    "En Tkinter, utilise Game.step(action) depuis le contrôleur."
                )

            try:
                self.step(action)
            except ValueError:
                # si action invalide, on redemande un coup
                continue

        self.winner.win()
        self.loser.lose()

        self.display()
        return self.winner

    def switch_player(self):
        """Change le joueur actuel."""
        self.current_player = self.player1 if self.current_player == self.player2 else self.player2

    def is_game_over(self):
        return self._is_over

    def get_current_player(self):
        return self.current_player

    def get_winner(self):
        return self._winner

    def get_loser(self):
        return self._loser


