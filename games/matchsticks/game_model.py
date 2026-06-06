"""
Game model for the Matchsticks game.

Rule:
    The player who takes the last match loses.
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.matchsticks.player import Player


class GameModel:
    """
    Store the game state and apply the Matchsticks rules.

    The model keeps track of:
    - the number of matches remaining,
    - the two players,
    - the current player's turn.

    It does not handle the graphical interface. The GUI is managed by the view
    and controller.
    """

    MAX_TAKE = 3

    def __init__(self, total_matches: int, player1: "Player", player2: "Player") -> None:
        """
        Initialize a new Matchsticks game.

        Args:
            total_matches: Initial number of matches. Must be at least 1.
            player1: First player.
            player2: Second player.

        Raises:
            ValueError: If total_matches is lower than 1.
        """
        if total_matches < 1:
            raise ValueError("total_matches must be >= 1.")

        self.original_nb = total_matches
        self.nb = total_matches
        self.players: list["Player"] = [player1, player2]
        self.current_player_index = 0

        for player in self.players:
            player.game = self

        self.shuffle_players()

    def shuffle_players(self) -> None:
        """
        Randomize the player order and reset the current player index.
        """
        random.shuffle(self.players)
        self.current_player_index = 0

    def reset(self) -> None:
        """
        Reset the game to its initial state.

        The number of matches is restored and the starting player is randomized
        again.
        """
        self.nb = self.original_nb
        self.shuffle_players()

    def step(self, action: int) -> None:
        """
        Apply one move by removing matches from the pile.

        Args:
            action: Number of matches to remove.

        Raises:
            ValueError: If the action is not between 1 and MAX_TAKE.
            ValueError: If the action is greater than the remaining matches.
        """
        if action < 1 or action > self.MAX_TAKE:
            raise ValueError(f"Invalid action: must be between 1 and {self.MAX_TAKE}.")
        if action > self.nb:
            raise ValueError("Invalid action: not enough matches remaining.")

        self.nb -= action

    def switch_player(self) -> None:
        """
        Switch to the other player.
        """
        self.current_player_index = 1 - self.current_player_index

    def is_game_over(self) -> bool:
        """
        Return True if no matches remain.
        """
        return self.nb == 0

    def get_current_player(self) -> "Player":
        """
        Return the player whose turn it is.
        """
        return self.players[self.current_player_index]

    def get_winner(self) -> "Player | None":
        """
        Return the winner if the game is over.

        Since the player who takes the last match loses, the winner is the
        other player.
        """
        if not self.is_game_over():
            return None
        return self.players[1 - self.current_player_index]

    def get_loser(self) -> "Player | None":
        """
        Return the loser if the game is over.

        The loser is the current player, because they took the last match.
        """
        if not self.is_game_over():
            return None
        return self.players[self.current_player_index]

    def play_automatic_game(self) -> None:
        """
        Play a complete automatic game without using the GUI.

        This method is used by the training and evaluation scripts. It repeatedly
        asks the current player for an action, applies the action, switches turns,
        and stops when no matches remain.

        At the end of the game, the winner and loser statistics are updated. For AI
        players, calling win() or lose() also records the final learning transition.
        """
        while not self.is_game_over():
            current_player = self.get_current_player()
            max_take = min(self.MAX_TAKE, self.nb)
            action = current_player.play(max_take)

            self.step(action)

            if self.is_game_over():
                winner = self.get_winner()
                loser = self.get_loser()

                winner.win()
                loser.lose()
                return

            self.switch_player()