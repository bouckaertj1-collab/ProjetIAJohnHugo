from __future__ import annotations

from games.pixelKart.model.movement import Action
from games.pixelKart.model.race import Race
from games.pixelKart.view.race_view import RaceView


class RaceController:
    """Coordinate the race model and the race view."""

    def __init__(self, race: Race, view: RaceView) -> None:
        """
        Initialize the race controller.

        Args:
            race: Race model instance.
            view: Race view instance.
        """
        self.race = race
        self.view = view

        self.view.bind_action(self.on_action_selected)
        self.view.set_circuit(self.race.circuit.to_dto().grid)

        self.refresh_view()
        self.play_ai_turns_if_needed()

    def on_action_selected(self, action: Action) -> None:
        """
        Handle a human action selected from the view.

        Args:
            action: Selected action.
        """
        if self.race.finished:
            return

        current_kart = self.race.get_current_kart()
        if current_kart.is_ai or not current_kart.is_alive:
            return

        self.race.play_current_turn(action)
        self.play_ai_turns_if_needed()

    def play_ai_turns_if_needed(self) -> None:
        """Play consecutive AI turns until a human turn or the end of the race."""
        while not self.race.finished:
            current_kart = self.race.get_current_kart()

            if not current_kart.is_alive:
                self.race.next_player()
                self.race.check_end_game()
                continue

            if not current_kart.is_ai:
                break

            self.race.play_current_ai_turn()

        self.refresh_view()

    def refresh_view(self) -> None:
        """Refresh the race view from the current model state."""
        self.view.update_view(
            race_dto=self.race.to_dto(),
            kart_dtos=[kart.to_dto() for kart in self.race.karts],
            current_kart_name=self.race.get_current_kart().name,
        )