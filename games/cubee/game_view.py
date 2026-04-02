import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.cubee.game_controller import GameController


class GameView(tk.Toplevel):
    """Tkinter view for the Cubee game."""

    EMPTY_COLOR = "white"
    P1_COLOR = "lightblue"
    P2_COLOR = "lightcoral"
    P1_CURRENT_COLOR = "deepskyblue"
    P2_CURRENT_COLOR = "tomato"

    CELL_STYLES: dict[str, dict[str, str]] = {
        "0": {"text": "", "bg": EMPTY_COLOR},
        "1": {"text": "1", "bg": P1_COLOR},
        "2": {"text": "2", "bg": P2_COLOR},
    }

    def __init__(self, parent: tk.Tk, controller: "GameController", size: int, cell_size: int = 4) -> None:
        """
        Initialize the game view.

        Args:
            parent: The parent window.
            controller: The game controller.
            size: The board size.
            cell_size: The button width for each cell.
        """
        super().__init__(parent)

        self.controller = controller
        self.size = size
        self.cell_size = cell_size

        self.title("Cubee")

        self.status_label = tk.Label(
            self,
            text="",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)

        self.score_label = tk.Label(
            self,
            text="Score: 0 - 0",
            font=("Arial", 11)
        )
        self.score_label.pack(pady=5)

        self.board_frame = tk.Frame(self)
        self.board_frame.pack(padx=10, pady=10)

        self.buttons: list[list[tk.Button]] = []
        self._create_board()

        self.reset_button = tk.Button(
            self,
            text="Reset",
            command=self.controller.reset
        )
        self.reset_button.pack(pady=10)

        self.finish_button = tk.Button(
            self,
            text="Quit",
            command=self.destroy
        )
        self.finish_button.pack(pady=5)

    def _create_board(self) -> None:
        """Create the board buttons."""
        for row in range(self.size):
            button_row: list[tk.Button] = []

            for col in range(self.size):
                button = tk.Button(
                    self.board_frame,
                    text="",
                    width=self.cell_size,
                    height=2,
                    command=lambda r=row, c=col: self.on_cell_click(r, c)
                )
                button.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(button)

            self.buttons.append(button_row)

    def update_view(self, state: dict) -> None:
        """
        Update the board and labels from the current game state.

        Args:
            state: The current game state.
        """
        board_str = state["board"]
        score_p1, score_p2 = state["score"]

        self.score_label.config(text=f"Score: {score_p1} - {score_p2}")

        if state["is_game_over"]:
            status = "Draw" if not state["winner"] else f"{state['winner']} wins!"
        else:
            current_player = (
                self.controller.model.player1
                if state["turn"] == 1
                else self.controller.model.player2
            )
            status = f"{current_player.name}'s turn"

        self.status_label.config(text=status)

        for index, cell in enumerate(board_str):
            row = index // self.size
            col = index % self.size
            self.buttons[row][col].config(**self.CELL_STYLES[cell])

        player1_row, player1_col = state["pos_p1"]
        player2_row, player2_col = state["pos_p2"]

        self.buttons[player1_row][player1_col].config(bg=self.P1_CURRENT_COLOR, text="P1")
        self.buttons[player2_row][player2_col].config(bg=self.P2_CURRENT_COLOR, text="P2",)

    def end_game(self, message: str, state: dict) -> None:
        """
        Show the final game state and display the end message.

        Args:
            message: The message to show.
            state: The final game state.
        """
        self.update_view(state)
        messagebox.showinfo("Game Over", message)

    def on_cell_click(self, row: int, col: int) -> None:
        """
        Handle a click on a board cell.

        Args:
            row: The clicked row.
            col: The clicked column.
        """
        self.controller.handle_cell_click(row, col)