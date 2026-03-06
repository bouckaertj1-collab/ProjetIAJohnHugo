import tkinter as tk
from tkinter import messagebox


class GameView:
    """
    Vue Tkinter du jeu Cubee.
    """

    EMPTY_COLOR = "white"
    P1_COLOR = "lightblue"
    P2_COLOR = "lightcoral"
    P1_CURRENT_COLOR = "deepskyblue"
    P2_CURRENT_COLOR = "tomato"

    def __init__(self, controller, size=5, cell_size=4):
        self.controller = controller
        self.size = size
        self.cell_size = cell_size

        self.root = tk.Tk()
        self.root.title("Cubee")

        self.status_label = tk.Label(self.root, text="Bienvenue dans Cubee", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.score_label = tk.Label(self.root, text="Score : 0 - 0", font=("Arial", 11))
        self.score_label.pack(pady=5)

        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(padx=10, pady=10)

        self.buttons = []
        for row in range(self.size):
            button_row = []
            for col in range(self.size):
                button = tk.Button(
                    self.board_frame,
                    text=" ",
                    width=self.cell_size,
                    height=2,
                    command=lambda r=row, c=col: self.on_cell_click(r, c)
                )
                button.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(button)
            self.buttons.append(button_row)

        self.reset_button = tk.Button(self.root, text="Reset", command=self.controller.reset)
        self.reset_button.pack(pady=10)

    def run(self) -> None:
        self.root.mainloop()

    def reset(self) -> None:
        self.status_label.config(text="Nouvelle partie")
        self.score_label.config(text="Score : 0 - 0")

    def update_view(self, state: dict) -> None:
        board_str = state["board"]
        score_p1, score_p2 = state["score"]

        self.score_label.config(text=f"Score : {score_p1} - {score_p2}")

        if state["is_game_over"]:
            if state["winner"] is None:
                self.status_label.config(text="Match nul")
            else:
                self.status_label.config(text=f"Gagnant : {state['winner']}")
        else:
            self.status_label.config(text=f"Tour du joueur {state['turn']}")

        for index, cell in enumerate(board_str):
            row = index // self.size
            col = index % self.size
            button = self.buttons[row][col]

            if cell == "0":
                button.config(text="", bg=self.EMPTY_COLOR)
            elif cell == "1":
                button.config(text="1", bg=self.P1_COLOR)
            elif cell == "2":
                button.config(text="2", bg=self.P2_COLOR)

        self.highlight_players(state)

    def highlight_players(self, state: dict) -> None:
        p1_row, p1_col = state["pos_p1"]
        p2_row, p2_col = state["pos_p2"]

        self.buttons[p1_row][p1_col].config(text="P1", bg=self.P1_CURRENT_COLOR)
        self.buttons[p2_row][p2_col].config(text="P2", bg=self.P2_CURRENT_COLOR)

    def end_game(self, message: str, state: dict) -> None:
        self.update_view(state)
        messagebox.showinfo("Fin de partie", message)

    def on_cell_click(self, row: int, col: int) -> None:
        state = self.controller.get_state_DTO()

        if state["is_game_over"]:
            return

        current_turn = state["turn"]

        if current_turn == 1:
            current_row, current_col = state["pos_p1"]
        else:
            current_row, current_col = state["pos_p2"]

        delta_row = row - current_row
        delta_col = col - current_col

        move = None
        if delta_row == -1 and delta_col == 0:
            move = "up"
        elif delta_row == 1 and delta_col == 0:
            move = "down"
        elif delta_row == 0 and delta_col == -1:
            move = "left"
        elif delta_row == 0 and delta_col == 1:
            move = "right"

        if move is not None:
            self.controller.handle_move(move)