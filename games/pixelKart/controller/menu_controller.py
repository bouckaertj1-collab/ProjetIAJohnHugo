from __future__ import annotations

from collections.abc import Callable
import tkinter as tk

from games.pixelKart.dao import circuit_dao as dao
from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.movement import Direction
from games.pixelKart.model.kart import HumanKart, RandomAIKart
from games.pixelKart.model.race import Race
from games.pixelKart.view.circuit_editor import CircuitEditor
from games.pixelKart.view.menu_view import MenuView


class MenuController:
    """Coordinate the PixelKart configuration menu."""

    KART_COLORS = ["red", "blue", "orange", "purple", "pink", "cyan", "brown", "white"]

    def __init__(
        self,
        root: tk.Misc,
        view: MenuView,
        on_start_race: Callable[[Race], None] | None = None,
    ) -> None:
        """
        Initialize the menu controller.

        Args:
            root: Root Tkinter widget.
            view: Menu view instance.
            on_start_race: Optional callback called when a valid race is created.
        """
        self.root = root
        self.view = view
        self.on_start_race = on_start_race

        self.view.bind_actions(
            play_callback=self.start_game,
            editor_callback=self.open_circuit_editor,
            refresh_callback=self.refresh_circuits,
        )

        self.refresh_circuits()

    def refresh_circuits(self) -> None:
        """Reload circuits from the DAO and refresh the menu view."""
        circuit_names = sorted(dao.get_all().keys())
        self.view.set_circuits(circuit_names)

        if circuit_names:
            self.view.set_message("")
        else:
            self.view.set_message("No circuit available. Create one in the editor.")

    def open_circuit_editor(self) -> None:
        """Open the circuit editor as a secondary window."""
        CircuitEditor(self.root, callback=self.on_circuit_chosen)

    def on_circuit_chosen(self, circuit_name: str) -> None:
        """
        Handle the circuit selected from the editor.

        Args:
            circuit_name: Name of the selected circuit.
        """
        self.refresh_circuits()
        if circuit_name:
            self.view.set_selected_circuit(circuit_name)

    def start_game(self) -> None:
        """Validate the menu configuration and create a race."""
        self.view.set_message("")

        try:
            human_players, ai_players, total_laps, circuit_name = self.view.get_config()
            total_players = human_players + ai_players

            if total_players <= 0:
                raise ValueError("You must select at least one player.")
            if total_laps <= 0:
                raise ValueError("The number of laps must be greater than 0.")
            if not circuit_name:
                raise ValueError("You must select a circuit.")

            circuit_dto = dao.get_by_name(circuit_name)
            if circuit_dto is None:
                raise ValueError(f"Unknown circuit: {circuit_name}")

            circuit = Circuit.from_dto(circuit_dto)
            start_positions = circuit.get_random_start_positions(total_players)
            karts = []

            for index in range(human_players):
                karts.append(
                    HumanKart(
                        name=f"Player {index + 1}",
                        color=self.KART_COLORS[index % len(self.KART_COLORS)],
                        position=start_positions[index],
                        direction=Direction.EAST,
                    )
                )

            for index in range(ai_players):
                color_index = human_players + index
                karts.append(
                    RandomAIKart(
                        name=f"AI {index + 1}",
                        color=self.KART_COLORS[color_index % len(self.KART_COLORS)],
                        position=start_positions[color_index],
                        direction=Direction.EAST,
                    )
                )

            race = Race(circuit=circuit, karts=karts, total_laps=total_laps)

            if self.on_start_race is not None:
                self.on_start_race(race)
            else:
                self.view.set_message("Race created successfully.")

        except ValueError as error:
            self.view.set_message(str(error))