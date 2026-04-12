"""Player classes for PixelKart."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .game_model.game_model import Action

if TYPE_CHECKING:
    from .game_model.game_model import GameModel


class Player:
    """Minimal base player for a PixelKart run."""

    def __init__(self, name: str, game: "GameModel | None" = None) -> None:
        self.name = name
        self.game = game
        self.nb_wins = 0
        self.nb_loses = 0
        self.best_score: int | None = None

    def play(self) -> Action:
        """Return the action chosen for the current turn."""
        return Action.WAIT

    def win(self, score: int) -> None:
        """Record a successful run."""
        self.nb_wins += 1
        if self.best_score is None or score < self.best_score:
            self.best_score = score

    def lose(self) -> None:
        """Record a failed run."""
        self.nb_loses += 1
