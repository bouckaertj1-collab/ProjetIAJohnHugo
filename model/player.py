"""
Define base player classes and simple AI players.
"""

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.game_model import GameModel


class Player:
    """
    class for a player.

    Attributes:
        name: Display name of the player.
        game: Optional reference to a game/model object.
        nb_wins: Number of wins.
        nb_loses: Number of losses.
    """

    def __init__(self, name: str, game: "GameModel | None" = None) -> None:
        """
        Initialize a player.

        Args:
            name: The player name.
            game: Optional game/model reference.
        """
        self.name = name
        self.game = game
        self.nb_wins = 0
        self.nb_loses = 0

    @property
    def nb_games(self) -> int:
        """
        Return the total number of games played.

        Returns:
            Total games = wins + losses.
        """
        return self.nb_wins + self.nb_loses

    @staticmethod
    def play() -> int:
        """
        Choose a random action between 1 and 3 (assignment requirement).
        """
        return random.randint(1, 3)

    def win(self) -> None:
        """Increment win counter."""
        self.nb_wins += 1

    def lose(self) -> None:
        """Increment lose counter."""
        self.nb_loses += 1

    def __str__(self) -> str:
        """Return a readable representation."""
        return f"{self.name} (W:{self.nb_wins} L:{self.nb_loses})"


class RandomAI(Player):
    """
    Simple AI player that picks a random number of matches (1 to 3).

    The controller may limit this value when fewer than three matches remain.
    """
    
    pass

