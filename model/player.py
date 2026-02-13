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
    def play(max_take: int = 3) -> int:
        """
        Choose a random action between 1 and `max_take`.

        Args:
            max_take: Maximum number of matches that can be taken this turn (>= 1).

        Returns:
            A random integer in [1, max_take].
        """
        return random.randint(1, max_take)

    def win(self) -> None:
        """Increment win counter."""
        self.nb_wins += 1

    def lose(self) -> None:
        """Increment lose counter."""
        self.nb_loses += 1

    def __str__(self) -> str:
        """Return a readable representation."""
        return (
        f"{self.name}\n"
        f"  Wins: {self.nb_wins}\n"
        f"  Losses: {self.nb_loses}\n"
        f"  Games played: {self.nb_games}"
    )


class RandomAI(Player):
    """
    Simple AI player that picks a random number of matches (1 to 3).

    The controller may limit this value when fewer than three matches remain.
    """

    pass

