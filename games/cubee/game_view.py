import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.cubee.game_controller import GameController


class GameView(tk.Toplevel):
    """
    Tkinter view for the Cubee game.

    The view displays the board, the score, and the current game status.
    It also converts mouse clicks into board coordinates and forwards them
    to the controller. The view does not apply game rules directly.
    """

    EMPTY_COLOR = "white"
    P1_COLOR = "lightblue"
    P2_COLOR = "lightcoral"
    P1_CURRENT_COLOR = "deepskyblue"
    P2_CURRENT_COLOR = "tomato"

    CELL_SIZE = 80
    BOARD_PADDING = 20

    def __init__(self, parent: tk.Tk, controller: "GameController", size: int) -> None:
        """
        Initialize the Cubee game window.

        Args:
            parent: Main Tkinter window.
            controller: Controller used to forward user actions.
            size: Board size.
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
            bg=self.EMPTY_COLOR,
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

        self.quit_button = tk.Button(
            self.controls_frame,
            text="Quit",
            font=("Arial", 12),
            width=10,
            command=self.destroy,
        )
        self.quit_button.grid(row=0, column=1, padx=10)

    def update_view(self, state_dto: dict) -> None:
        """
        Refresh the board, score, and status label.

        Args:
            state_dto: Current game state provided by the controller.
        """
        board_str = state_dto["board"]
        score_p1, score_p2 = state_dto["score"]

        self.score_label.config(text=f"Score: {score_p1} - {score_p2}")

        if state_dto["is_game_over"]:
            if not state_dto["winner"]:
                status = "Draw"
            else:
                status = f"{state_dto['winner']} wins!"
        else:
            status = f"{state_dto['current_player_name']}'s turn"

        self.status_label.config(text=status)

        self.canvas.delete("all")

        player1_row, player1_col = state_dto["pos_p1"]
        player2_row, player2_col = state_dto["pos_p2"]

        for index, cell in enumerate(board_str):
            row = index // self.size
            col = index % self.size

            x1 = col * self.CELL_SIZE
            y1 = row * self.CELL_SIZE
            x2 = x1 + self.CELL_SIZE
            y2 = y1 + self.CELL_SIZE

            if cell == "0":
                bg = self.EMPTY_COLOR
                text = ""
            elif cell == "1":
                bg = self.P1_COLOR
                text = "1"
            else:
                bg = self.P2_COLOR
                text = "2"

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

    def end_game(self, status_message: str, state_dto: dict) -> None:
        """
        Display the final board state and show the end-game message.

        Args:
            status_message: Final message built by the controller.
            state_dto: Final game state used to refresh the board.
        """
        self.update_view(state_dto)
        messagebox.showinfo("Game Over", status_message)

    def on_canvas_click(self, event: tk.Event) -> None:
        """
        Convert a mouse click into board coordinates.

        Args:
            event: Tkinter mouse event containing the click position.
        """
        row = event.y // self.CELL_SIZE
        col = event.x // self.CELL_SIZE

        if 0 <= row < self.size and 0 <= col < self.size:
            self.controller.handle_cell_click(row, col)