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

    CELL_SIZE = 80
    BOARD_PADDING = 20

    CELL_STYLES: dict[str, dict[str, str]] = {
        "0": {"text": "", "bg": EMPTY_COLOR},
        "1": {"text": "1", "bg": P1_COLOR},
        "2": {"text": "2", "bg": P2_COLOR},
    }

    def __init__(self, parent: tk.Tk, controller: "GameController", size: int) -> None:
        """
        Initialize the game view.

        Args:
            parent: The parent window.
            controller: The game controller.
            size: The board size.
        """
        super().__init__(parent)

        self.controller = controller
        self.size = size

        board_pixel_size = self.size * self.CELL_SIZE
        window_width = board_pixel_size + 2 * self.BOARD_PADDING + 80
        window_height = board_pixel_size + 230

        self.title("Cubee")
        self.geometry(f"{window_width}x{window_height}")
        self.resizable(False, False)

        self.status_label = tk.Label(
            self,
            text="",
            font=("Arial", 18, "bold"),
        )
        self.status_label.pack(pady=(20, 8))

        self.score_label = tk.Label(
            self,
            text="Score: 0 - 0",
            font=("Arial", 15),
        )
        self.score_label.pack(pady=5)

        self.canvas = tk.Canvas(
            self,
            width=board_pixel_size,
            height=board_pixel_size,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.pack(padx=self.BOARD_PADDING, pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(pady=10)

        self.reset_button = tk.Button(
            self.controls_frame,
            text="Reset",
            font=("Arial", 12),
            width=10,
            command=self.controller.reset,
        )
        self.reset_button.grid(row=0, column=0, padx=10)

        self.finish_button = tk.Button(
            self.controls_frame,
            text="Quit",
            font=("Arial", 12),
            width=10,
            command=self.destroy,
        )
        self.finish_button.grid(row=0, column=1, padx=10)

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

        self.canvas.delete("all")

        player1_row, player1_col = state["pos_p1"]
        player2_row, player2_col = state["pos_p2"]

        for index, cell in enumerate(board_str):
            row = index // self.size
            col = index % self.size

            x1 = col * self.CELL_SIZE
            y1 = row * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1 + self.CELL_SIZE

            style = self.CELL_STYLES[cell]
            bg = style["bg"]
            text = style["text"]

            if (row, col) == (player1_row, player1_col):
                bg = self.P1_CURRENT_COLOR
                text = "P1"
            elif (row, col) == (player2_row, player2_col):
                bg = self.P2_CURRENT_COLOR
                text = "P2"

            self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill=bg,
                outline="black",
                width=2,
            )

            self.canvas.create_text(
                x1 + self.CELL_SIZE / 2,
                y1 + self.CELL_SIZE / 2,
                text=text,
                font=("Arial", 14, "bold"),
            )

    def end_game(self, message: str, state: dict) -> None:
        """
        Show the final game state and display the end message.

        Args:
            message: The message to show.
            state: The final game state.
        """
        self.update_view(state)
        messagebox.showinfo("Game Over", message)

    def on_canvas_click(self, event: tk.Event) -> None:
        """
        Handle a click on the board canvas.

        Args:
            event: Tkinter mouse event.
        """
        row = event.y // self.CELL_SIZE
        col = event.x // self.CELL_SIZE

        if 0 <= row < self.size and 0 <= col < self.size:
            self.controller.handle_cell_click(row, col)