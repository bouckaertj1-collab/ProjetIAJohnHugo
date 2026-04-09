from __future__ import annotations

import tkinter as tk

from games.pixelKart.model.race import Race
from games.pixelKart.view.menu_view import MenuView
from games.pixelKart.view.race_view import RaceView
from games.pixelKart.controller.menu_controller import MenuController
from games.pixelKart.controller.race_controller import RaceController


class GameController:
    """Main controller of PixelKart."""

    def __init__(self, parent: tk.Misc) -> None:
        """
        Initialize the PixelKart controller.

        Args:
            parent: Parent Tkinter widget.
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("PixelKart")
        self.window.geometry("1100x700")

        self.current_view: tk.Widget | None = None
        self.current_controller = None

        self.show_menu()

    def show_menu(self) -> None:
        """Display the game configuration menu."""
        self._clear_current_view()

        view = MenuView(self.window)
        self.current_view = view
        self.current_controller = MenuController(
            root=self.window,
            view=view,
            on_start_race=self.show_race,
        )

    def show_race(self, race: Race) -> None:
        """
        Display the race screen.

        Args:
            race: Race model to display.
        """
        self._clear_current_view()

        view = RaceView(self.window)
        self.current_view = view
        self.current_controller = RaceController(race=race, view=view)

    def start(self) -> None:
        """Show the PixelKart window."""
        self.window.grab_set()
        self.window.focus_set()

    def _clear_current_view(self) -> None:
        """Destroy the currently displayed view, if any."""
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None