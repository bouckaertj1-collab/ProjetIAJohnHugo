"""
Tkinter view for the Matchsticks game.

The view is responsible for displaying the game state and user controls.
It does not access the model directly; it gets the required information from
the controller.
"""

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.matchsticks.game_controller import GameController


class GameView(tk.Toplevel):
    """
    Graphical window for the Matchsticks game.
    """

    def __init__(self, parent: tk.Tk, controller: "GameController") -> None:
        """
        Create the game window and its widgets.

        Args:
            parent: Parent Tkinter window.
            controller: Controller used to interact with the game logic.
        """
        super().__init__(parent)
        self.controller = controller

        self.title("Jeu des allumettes")
        self.resizable(False, False)
        self.configure(padx=24, pady=24)

        self.message_label = tk.Label(self, text="", font=("Arial", 12, "bold"))
        self.message_label.pack(pady=(0, 10))

        self.canvas = tk.Canvas(
            self,
            width=520,
            height=240,
            bg="#f5f5f5",
            highlightthickness=0,
        )
        self.canvas.pack(pady=(0, 12))

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack()

        self._create_action_buttons()
        self.update_view()

    def update_view(self) -> None:
        """
        Refresh the displayed matches, button states, and status message.
        """
        nb_matches = self.controller.get_nb_matches()

        self.canvas.delete("all")
        self._draw_matches(nb_matches)

        self._update_action_buttons_state(nb_matches)
        self.message_label.config(text=self.controller.get_status_message())

    def _create_action_buttons(self) -> None:
        """
        Create the buttons used by the human player to take matches.

        The controller binds the actual commands after the buttons are created.
        """
        button_options = {"width": 12, "height": 2}

        self.btn1 = tk.Button(self.buttons_frame, text="Prendre 1", **button_options)
        self.btn2 = tk.Button(self.buttons_frame, text="Prendre 2", **button_options)
        self.btn3 = tk.Button(self.buttons_frame, text="Prendre 3", **button_options)

        for button in (self.btn1, self.btn2, self.btn3):
            button.pack(side=tk.LEFT, padx=8)

    def _update_action_buttons_state(self, nb_matches: int) -> None:
        """
        Enable or disable action buttons depending on the number of matches left.
        """
        self.btn1.config(state=("normal" if nb_matches >= 1 else "disabled"))
        self.btn2.config(state=("normal" if nb_matches >= 2 else "disabled"))
        self.btn3.config(state=("normal" if nb_matches >= 3 else "disabled"))

    def _draw_matches(self, nb_matches: int) -> None:
        """
        Draw the remaining matches on the canvas.
        """
        matches_per_row = 21
        x_start, y_start = 20, 24

        stick_width = 6
        stick_height = 66
        head_radius = 7
        gap = 23

        for index in range(nb_matches):
            row = index // matches_per_row
            col = index % matches_per_row

            x = x_start + col * gap
            y = y_start + row * (stick_height + 20)

            self.canvas.create_oval(
                x - head_radius,
                y - head_radius,
                x + head_radius,
                y + head_radius,
                fill="#d9534f",
                outline="#b13f3b",
            )

            self.canvas.create_rectangle(
                x - stick_width // 2,
                y,
                x + stick_width // 2,
                y + stick_height,
                fill="#deb887",
                outline="#2f2f2f",
            )

    def end_game(self) -> None:
        """
        Replace action buttons with end-of-game controls.
        """
        self._clear_buttons()

        restart_button = tk.Button(
            self.buttons_frame,
            text="Restart",
            command=self.controller.reset_game,
            width=18,
            height=2,
        )
        restart_button.pack(side=tk.LEFT, padx=6)

        end_button = tk.Button(
            self.buttons_frame,
            text="End",
            command=self.controller.show_stats,
            width=18,
            height=2,
        )
        end_button.pack(side=tk.LEFT, padx=6)

    def reset(self) -> None:
        """
        Restore the default action buttons and refresh the display.
        """
        self._clear_buttons()
        self._create_action_buttons()
        self.update_view()

    def _clear_buttons(self) -> None:
        """
        Remove all buttons from the button area.
        """
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()