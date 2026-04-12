"""Controller for the PixelKart game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .game_model.game_model import Action, GameModel

if TYPE_CHECKING:
    from .game_view import GameView


class GameController:
    """Connect the PixelKart model to its Tkinter view."""

    def __init__(self, model: GameModel | None = None, view: "GameView | None" = None) -> None:
        """
        Initialize the controller.

        Args:
            model: Existing model, or None to create a one-player race.
            view: Optional view attached after creation.
        """
        self.model = model or GameModel()
        self.view = view
        self._end_game_displayed = False

    def start(self) -> None:
        """Start or refresh the current race."""
        self._end_game_displayed = False
        self._update_view()

    def reset(self) -> None:
        """Reset the current race with the same players."""
        self.model.reset()
        self.start()

    def new_game(self, player_count: int = 1,laps_count: int = 1) -> None:
        """
        Start a new race with a chosen number of players.

        Args:
            player_count: Number of human players. Must be at least 1.
        """

        if player_count < 1:
            raise ValueError("At least one player required")

        player_names = tuple(f"Player {index + 1}" for index in range(player_count))

        self.model = GameModel(
            track=self.model.track,
            total_laps=laps_count,
            displayable=self.model.displayable,
            player_names=player_names,
        )
        self.start()

    def handle_action(self, action: str | Action) -> bool:
        """
        Apply one turn action for the current player.

        Returns:
            True if the action was applied, False otherwise.
        """
        success = self.model.step(action)
        if not success:
            return False

        self._update_view()

        if self.model.is_game_over:
            self.handle_end_game()

        return True

    def handle_end_game(self) -> None:
        """Notify the view when the race is over."""
        if self._end_game_displayed:
            return

        self._end_game_displayed = True
        if self.view is not None:
            self.view.end_game(self.get_status_message(), self.get_state_DTO())

    def get_status_message(self) -> str:
        """Return the status message displayed by the view."""
        if self.model.is_game_over:
            winner = self.model.winner
            if winner is None:
                return "Course terminee: aucun joueur n'a termine."
            return f"{winner.name} gagne en {winner.finish_time} tours."

        current = self.model.current_kart
        return (
            f"Tour de {current.name} | "
            f"Vitesse: {current.speed} px/tour | "
            f"Tours: {current.laps_completed}/{self.model.total_laps}"
        )

    def get_state_DTO(self) -> dict:
        """Return the current model state."""
        return self.model.get_state_dto()

    def get_player_count(self) -> int:
        """Return the number of players in the current race."""
        return len(self.model.karts)
    
    def get_laps_count(self)-> int:
        return self.model.total_laps

    def _update_view(self) -> None:
        """Refresh the attached view."""
        if self.view is not None:
            self.view.update_view(self.get_state_DTO())
