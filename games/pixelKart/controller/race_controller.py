from __future__ import annotations

from collections.abc import Callable

from games.pixelKart.model.race import Race
from games.pixelKart.view.race_view import RaceView


class RaceController:
    """Coordinate the race model and race view."""

    def __init__(
        self,
        race: Race,
        view: RaceView,
        on_back_to_menu: Callable[[], None] | None = None,
    ) -> None:
        """
        Initialize the race controller.

        Args:
            race: Race model to control.
            view: Race view to update.
            on_back_to_menu: Callback used to return to the menu.
        """
        self.race = race
        self.view = view
        self.on_back_to_menu = on_back_to_menu
        self.ai_turns_without_human = 0
        self.max_ai_turns_without_human = 2000

        self.view.bind_action(self.on_action_selected)
        self.view.bind_back_to_menu(self.back_to_menu)
        self.view.set_circuit(self.race.circuit.to_dto()["grid"])

        self.refresh_view()
        self.schedule_ai_turn_if_needed()

    def on_action_selected(self, action: str) -> None:
        """
        Play a human action selected in the view.

        Args:
            action: Action selected by the human player.
        """
        if self.race.finished:
            self.refresh_view()
            return

        current_kart = self.race.get_current_kart()

        if current_kart.is_ai or not current_kart.is_alive or current_kart.has_finished:
            return

        self.ai_turns_without_human = 0

        self.race.play_current_turn(action)
        self.refresh_view()

        self.schedule_ai_turn_if_needed()

    def back_to_menu(self) -> None:
        """Return to the PixelKart menu."""
        if self.on_back_to_menu is not None:
            self.on_back_to_menu()

    def schedule_ai_turn_if_needed(self) -> None:
        """Schedule an AI turn when the current kart is AI-controlled."""
        if self.race.finished:
            self.refresh_view()
            return

        current_kart = self.race.get_current_kart()

        if not current_kart.is_alive or current_kart.has_finished:
            self.race.next_player()
            self.race.check_end_game()
            self.refresh_view()
            self.schedule_ai_turn_if_needed()
            return

        if current_kart.is_ai:
            self.view.after(300, self.play_one_ai_turn)
        else:
            self.refresh_view()

    def play_one_ai_turn(self) -> None:
        """Play one AI turn and schedule the next turn if needed."""
        if self.race.finished:
            self.refresh_view()
            return

        current_kart = self.race.get_current_kart()

        if not current_kart.is_alive or current_kart.has_finished:
            self.race.next_player()
            self.race.check_end_game()
            self.refresh_view()
            self.schedule_ai_turn_if_needed()
            return

        if not current_kart.is_ai:
            self.refresh_view()
            return

        self.ai_turns_without_human += 1

        if self.ai_turns_without_human >= self.max_ai_turns_without_human:
            self.race.finished = True
            self.race.winner_name = None
            self.refresh_view()
            return

        self.race.play_current_ai_turn()
        self.refresh_view()

        self.schedule_ai_turn_if_needed()

    def refresh_view(self) -> None:
        """Update the view from the current race state."""
        self.view.update_view(
            race_dto=self.race.to_dto(),
            kart_dtos=[kart.to_dto() for kart in self.race.karts],
            current_kart_name=self.race.get_current_kart().name,
        )