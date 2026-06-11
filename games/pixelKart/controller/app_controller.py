"""
Control the main PixelKart flow.

This module contains the AppController class. It manages the PixelKart window,
shows the menu, opens the circuit editor, creates a race from the menu choices,
and switches from the menu screen to the race screen.

It connects the high-level parts of PixelKart:
- circuit loading;
- kart creation;
- Q-table loading for Q-learning karts;
- race creation;
- screen changes between menu, editor and race.
"""

from __future__ import annotations

import tkinter as tk

from games.pixelKart.dao import circuit_dao
from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.kart import HumanKart, QLearningKart, RandomAIKart
from games.pixelKart.dao.q_table_service import load_q_table_for_circuit
from games.pixelKart.model.race import Race
from games.pixelKart.view.pixelkart_window import PixelKartWindow
from games.pixelKart.view.circuit_editor import CircuitEditor
from games.pixelKart.view.menu_view import MenuView
from games.pixelKart.view.race_view import RaceView
from games.pixelKart.controller.race_controller import RaceController


class AppController:
    """Control the main PixelKart window and screen changes."""

    KART_COLORS = ["red", "blue", "orange", "purple", "pink", "cyan", "brown", "white"]

    def __init__(self, parent: tk.Misc) -> None:
        """
        Initialize the PixelKart controller.

        Args:
            parent: Parent Tkinter widget.
        """
        self.parent = parent
        self.window = PixelKartWindow(parent)

        self.current_view: tk.Widget | None = None
        self.current_controller = None

        self.show_menu()

    def show_menu(self) -> None:
        """Display the PixelKart menu."""
        self._clear_current_view()

        view = MenuView(self.window)
        self.current_view = view
        self.current_controller = None

        view.bind_actions(
            play_callback=self.start_game,
            editor_callback=self.open_circuit_editor,
            refresh_callback=self.refresh_circuits,
        )

        self.refresh_circuits()

    def refresh_circuits(self) -> None:
        """Reload available circuits in the menu."""
        circuit_names = sorted(circuit_dao.get_all().keys())
        self.current_view.set_circuits(circuit_names)
        self.current_view.set_message("")

    def open_circuit_editor(self) -> None:
        """Open the circuit editor window."""
        CircuitEditor(self.window, callback=self.on_circuit_chosen)

    def on_circuit_chosen(self, circuit_name: str) -> None:
        """
        Select the circuit chosen in the editor.

        Args:
            circuit_name: Name of the circuit selected for the race.
        """
        self.refresh_circuits()
        self.current_view.set_selected_circuit(circuit_name)

    def start_game(self) -> None:
        """
        Create and display a race using the current menu configuration.

        The method reads the selected players, circuit and lap count, creates the
        corresponding model objects, then opens the race screen.
        """
        menu_view = self.current_view
        menu_view.set_message("")

        try:
            human_player_count, random_ai_count, ql_ai_count, total_laps, circuit_name = (
                menu_view.get_race_config()
            )
            total_players = human_player_count + random_ai_count + ql_ai_count

            if total_players <= 0:
                raise ValueError("You must select at least one player.")

            circuit = Circuit.from_dto(circuit_dao.get_by_name(circuit_name))
            start_positions = circuit.get_random_start_positions(total_players)

            shared_q_table = {}
            if ql_ai_count > 0:
                shared_q_table = load_q_table_for_circuit(circuit.name)

            karts = []

            for player_number in range(1, human_player_count + 1):
                index = len(karts)
                karts.append(
                    HumanKart(
                        name=f"Player {player_number}",
                        color=self.KART_COLORS[index % len(self.KART_COLORS)],
                        position=start_positions[index],
                        direction="EAST",
                    )
                )

            for ai_number in range(1, random_ai_count + 1):
                index = len(karts)
                karts.append(
                    RandomAIKart(
                        name=f"Random AI {ai_number}",
                        color=self.KART_COLORS[index % len(self.KART_COLORS)],
                        position=start_positions[index],
                        direction="EAST",
                    )
                )

            for ai_number in range(1, ql_ai_count + 1):
                index = len(karts)
                karts.append(
                    QLearningKart(
                        name=f"QLearning AI {ai_number}",
                        color=self.KART_COLORS[index % len(self.KART_COLORS)],
                        position=start_positions[index],
                        direction="EAST",
                        q_table=shared_q_table,
                        epsilon=0.0,
                        alpha=0.2,
                        gamma=0.95,
                    )
                )

            race = Race(circuit=circuit, karts=karts, total_laps=total_laps)
            self.show_race(race)

        except ValueError as error:
            menu_view.set_message(str(error))
            
    def show_race(self, race: Race) -> None:
        """
        Display the race screen.

        Args:
            race: Race model to control and display.
        """
        self._clear_current_view()

        view = RaceView(self.window)
        self.current_view = view
        self.current_controller = RaceController(
            race=race,
            view=view,
            on_back_to_menu=self.show_menu,
        )

    def start(self) -> None:
        """Bring the PixelKart window to the front."""
        self.window.lift()
        self.window.focus_set()

    def _clear_current_view(self) -> None:
        """Destroy the current screen if one is displayed."""
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None
