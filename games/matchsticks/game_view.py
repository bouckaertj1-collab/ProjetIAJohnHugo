"""
Tkinter view for the matchstick game.

Design choice:
    The view does NOT read the model directly. It queries the controller.
"""

import tkinter as tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.matchsticks.game_controller import GameController


class GameView(tk.Toplevel):
    """
    Tkinter GUI window.

    Responsibilities:
        - Display the remaining matches
        - Display status messages (turn / winner)
        - Provide buttons for human actions
        - Delegate all game logic to the controller
    """

    def __init__(self,parent, controller: "GameController") -> None:
        """
        Create the main window and widgets.

        Args:
            controller: The controller that coordinates model/view.
        """
        super().__init__(parent)
        self.controller = controller

        self.title("Jeu des allumettes")
        self.resizable(False, False)  
        self.configure(padx=24, pady=24)

        self.message_label = tk.Label(self, text="", font=("Arial", 12, "bold"))
        self.message_label.pack(pady=(0, 10))

        self.canvas = tk.Canvas(self, width=520, height=240, bg="#f5f5f5", highlightthickness=0)
        self.canvas.pack(pady=(0, 12))

        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack()

        btn_size = {"width": 12, "height": 2}
        self.btn1 = tk.Button(self.buttons_frame, text="Prendre 1", command=lambda: None, **btn_size)
        self.btn2 = tk.Button(self.buttons_frame, text="Prendre 2", command=lambda: None, **btn_size)
        self.btn3 = tk.Button(self.buttons_frame, text="Prendre 3", command=lambda: None, **btn_size)

        self.btn1.pack(side=tk.LEFT, padx=8)
        self.btn2.pack(side=tk.LEFT, padx=8)
        self.btn3.pack(side=tk.LEFT, padx=8)

        self.update_view()

    def update_view(self) -> None:
        """
        Refresh the canvas, buttons state, and message label.

        The view asks the controller for:
            - number of matches remaining
            - status message
        """
        nb = self.controller.get_nb_matches()

        self.canvas.delete("all")
        self.draw_matches(nb)

        self.btn1.config(state=("normal" if nb >= 1 else "disabled"))
        self.btn2.config(state=("normal" if nb >= 2 else "disabled"))
        self.btn3.config(state=("normal" if nb >= 3 else "disabled"))

        self.message_label.config(text=self.controller.get_status_message())


    def draw_matches(self, nb: int) -> None:
        """
        Draw `nb` matches on the canvas.

        Args:
            nb: Number of matches to draw (>= 0).
        """
        per_row = 21
        x0, y0 = 20, 24

        stick_w = 6
        stick_h = 46
        head_r = 7
        gap = 23

        for i in range(nb):
            row = i // per_row  
            col = i % per_row

            x = x0 + col * gap
            y = y0 + row * (stick_h + 20)

            self.canvas.create_oval(
                x - head_r, y - head_r,
                x + head_r, y + head_r,
                fill="#d9534f", outline="#b13f3b"
            )

            self.canvas.create_rectangle(
                x - stick_w // 2, y,
                x + stick_w // 2, y + stick_h,
                fill="#deb887", outline="#2f2f2f"
            )

    def end_game(self) -> None:
        """
        Switch the UI to "end of game" mode.

        This method updates the interface once the game is finished.
        It removes the action buttons (take 1/2/3 matches) and replaces
        them with:
            - a "Restart" button to start a new game
            - a "Terminate" button to display final statistics and exit

        Postconditions:
            - Action buttons are removed
            - End-of-game control buttons are displayed
        """
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        reset_btn = tk.Button(
            self.buttons_frame,
            text="Restart",
            command=self.controller.reset_game,
            width=18,
            height=2
        )
        reset_btn.pack(side=tk.LEFT, padx=6)

        terminate_btn = tk.Button(
            self.buttons_frame,
            text="End",
            command=self.controller.show_stats,
            width=18,
            height=2
        )
        terminate_btn.pack(side=tk.LEFT, padx=6)
    
    def reset(self) -> None:
        """
        Restore the default UI (buttons 1/2/3).

        Note:
            The controller should re-bind button commands because buttons are recreated.
        """
        for widget in self.buttons_frame.winfo_children():
            widget.destroy()

        btn_kwargs = {"width": 12, "height": 2}
        self.btn1 = tk.Button(self.buttons_frame, text="Prendre 1", command=lambda: None, **btn_kwargs)
        self.btn2 = tk.Button(self.buttons_frame, text="Prendre 2", command=lambda: None, **btn_kwargs)
        self.btn3 = tk.Button(self.buttons_frame, text="Prendre 3", command=lambda: None, **btn_kwargs)

        self.btn1.pack(side=tk.LEFT, padx=8)
        self.btn2.pack(side=tk.LEFT, padx=8)
        self.btn3.pack(side=tk.LEFT, padx=8)

        self.update_view()
