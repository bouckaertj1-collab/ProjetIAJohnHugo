from __future__ import annotations

from collections.abc import Callable

from games.PixelKart.model.race import Race
from games.PixelKart.view.race_view import RaceView
from games.PixelKart.dao.q_table_service import *


class RaceController:
    """Coordinate the race model and the race view."""

    def __init__(
        self,
        race: Race,
        view: RaceView,
        on_back_to_menu: Callable[[], None] | None = None,
    ) -> None:
        """
        Initialize the race controller.

        Args:
            race: Race model instance.
            view: Race view instance.
            on_back_to_menu: Callback used to go back to the menu.
        """
        self.race = race
        self.view = view
        self.on_back_to_menu = on_back_to_menu

        self.view.bind_action(self.handle_human_turn)
        self.view.bind_back_to_menu(self.back_to_menu)
        self.view.set_circuit(self.race.circuit.to_dto()["grid"])

        self.refresh_view()
        self.step_game(self.race.get_current_kart)


    def step_game(self, action: str | None = None) -> None:
        """"""
        if self.race.finished:
            return

        kart = self.race.get_current_kart()

        if kart.is_ai:
            self.race.play_current_turn()
        else:
            if action is None:
                return 
            self.race.play_current_turn(action)

    
        while not self.race.finished and self.race.get_current_kart().is_ai:
            kart = self.race.get_current_kart()

            if not kart.is_alive:
                self.race.next_player()
                self.race.check_end_game()
                continue

            self.race.play_current_turn()
        
        self.refresh_view()

    def back_to_menu(self) -> None:
        """Ask the parent controller to go back to the menu."""
        if self.on_back_to_menu is not None:
            self.on_back_to_menu()

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
