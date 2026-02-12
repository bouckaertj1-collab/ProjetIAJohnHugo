"""
Game model for the matches game.

Rule:
    The player who takes the last match loses.
"""

import random
from typing import Optional

from model.player import Player


class GameModel:
    """
    Store the game state and apply the game rules.

    Attributes:
        original_nb: Initial number of matches at the start of each game.
        nb: Current number of matches remaining.
        players: List of two players.
        current_player: Index (0 or 1) of the current player in `players`.
    """

    def __init__(self, total_matches: int, player1: Player, player2: Player) -> None:
        """
        Initialize the model.

        Args:
            total_matches: Initial number of matches (> 0).
            player1: First player.
            player2: Second player.

        Postconditions:
            - nb is set to total_matches.
            - players are shuffled to randomize who starts.
            - each player's `game` reference points to this model.
        """
        self.original_nb = total_matches
        self.nb = total_matches

        self.players = [player1, player2]
        for p in self.players:
            p.game = self

        self.current_player = 0
        self.shuffle()

    def shuffle(self) -> None:
        """
        Randomize player order and reset current player index.

        Postconditions:
            - players order may change.
            - current_player is set to 0.
        """
        random.shuffle(self.players)
        self.current_player = 0

    def reset(self) -> None:
        """
        Reset the game to its initial state.

        Postconditions:
            - nb is restored to original_nb.
            - players are shuffled again.
        """
        self.nb = self.original_nb
        self.shuffle()

    def step(self, action: int) -> None:
        """
        Apply one move: remove matches from the pile.

        Args:
            action: Number of matches to remove (must be 1..3 and <= nb).

        Raises:
            ValueError: If action is not in [1, 3] or action > nb.

        Postconditions:
            - nb is decreased by `action`.
        """
        if action < 1 or action > 3:
            raise ValueError("Invalid action: must be 1, 2 or 3.")
        if action > self.nb:
            raise ValueError("Invalid action: not enough matches remaining.")
        self.nb -= action

    def switch_player(self) -> None:
        """
        Switch to the other player.

        Postconditions:
            - current_player becomes 1 - current_player.
        """
        self.current_player = 1 - self.current_player

    def is_game_over(self) -> bool:
        """
        Check if the game is finished.

        Returns:
            True if no matches remain, else False.
        """
        return self.nb == 0

    def get_current_player(self) -> Player:
        """
        Get the player whose turn it is.

        Returns:
            The current Player instance.
        """
        return self.players[self.current_player]

    def get_winner(self) -> Optional[Player]:
        """
        Get the winner if the game is over.

        Since taking the last match loses, the winner is the player who is NOT
        the current player once nb reaches 0.

        Returns:
            The winner Player if game over, otherwise None.
        """
        if not self.is_game_over():
            return None
        return self.players[1 - self.current_player]

    def get_loser(self) -> Optional[Player]:
        """
        Get the loser if the game is over.

        Returns:
            The loser Player if game over, otherwise None.
        """
        if not self.is_game_over():
            return None
        return self.players[self.current_player]
