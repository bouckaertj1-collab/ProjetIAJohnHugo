from __future__ import annotations

import tkinter as tk

from games.pixelKart.dao import circuit_dao
from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.kart import HumanKart, RandomAIKart
from games.pixelKart.model.race import Race
from games.pixelKart.view.circuit_editor import CircuitEditor
from games.pixelKart.view.menu_view import MenuView
from games.pixelKart.view.race_view import RaceView
from games.pixelKart.controller.race_controller import RaceController


class AppController:
    """Main controller of PixelKart."""

    KART_COLORS = ["red", "blue", "orange", "purple", "pink", "cyan", "brown", "white"]

    def __init__(self, parent: tk.Misc) -> None:
        """
        Initialize the PixelKart controller.

        Args:
            parent: Parent Tkinter widget.
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("PixelKart")
        self._center_window()

        self.current_view: tk.Widget | None = None
        self.current_controller = None

        self.show_menu()

    def show_menu(self) -> None:
        """Display the game configuration menu."""
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
        """Reload circuits from the DAO and refresh the menu view."""
        if not isinstance(self.current_view, MenuView):
            return

        circuit_names = sorted(circuit_dao.get_all().keys())
        self.current_view.set_circuits(circuit_names)

        if circuit_names:
            self.current_view.set_message("")
        else:
            self.current_view.set_message("No circuit available. Create one in the editor.")

    def open_circuit_editor(self) -> None:
        """Open the circuit editor as a secondary window."""
        CircuitEditor(self.window, callback=self.on_circuit_chosen)

    def on_circuit_chosen(self, circuit_name: str) -> None:
        """
        Handle the circuit selected from the editor.

        Args:
            circuit_name: Name of the selected circuit.
        """
        self.refresh_circuits()

        if isinstance(self.current_view, MenuView) and circuit_name:
            self.current_view.set_selected_circuit(circuit_name)

    def start_game(self) -> None:
        """Validate the menu configuration and create a race."""
        if not isinstance(self.current_view, MenuView):
            return

        self.current_view.set_message("")

        try:
            human_players, ai_players, total_laps, circuit_name = self.current_view.get_config()
            total_players = human_players + ai_players

            if not circuit_name:
                raise ValueError("You must select a circuit.")

            circuit_dto = circuit_dao.get_by_name(circuit_name)
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
                        direction="EAST",
                    )
                )

            for index in range(ai_players):
                color_index = human_players + index
                karts.append(
                    RandomAIKart(
                        name=f"AI {index + 1}",
                        color=self.KART_COLORS[color_index % len(self.KART_COLORS)],
                        position=start_positions[color_index],
                        direction="EAST",
                    )
                )

            race = Race(circuit=circuit, karts=karts, total_laps=total_laps)
            self.show_race(race)

        except ValueError as error:
            self.current_view.set_message(str(error))

    def show_race(self, race: Race) -> None:
        """
        Display the race screen.

        Args:
            race: Race model to display.
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
        """Show the PixelKart window."""
        self.window.grab_set()
        self.window.focus_set()

    def _clear_current_view(self) -> None:
        """Destroy the currently displayed view, if any."""
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

    def _center_window(self, width: int = 1100, height: int = 700) -> None:
        """Center the PixelKart window on screen."""
        self.window.update_idletasks()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.window.geometry(f"{width}x{height}+{x}+{y}")