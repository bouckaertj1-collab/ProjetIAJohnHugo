"""
Controller for the Matchsticks game.

The controller connects the model and the Tkinter view. It receives user
actions from the GUI, applies them to the model, updates the display, and
triggers AI turns when needed.
"""

import tkinter.messagebox as mb

from games.matchsticks.game_model import GameModel
from games.matchsticks.game_view import GameView
from games.matchsticks.player import AI, HumanGUI, Player


class GameController:
    """
    Coordinate the Matchsticks model, view, and players.
    """

    AI_TRAINING_FILE = "games/matchsticks/bob_training.json"
    AI_MOVE_DELAY_MS = 600

    def __init__(self, p1: Player, p2: Player, total_matches: int, parent) -> None:
        """
        Create the model and view for a graphical Matchsticks game.

        Args:
            p1: First player.
            p2: Second player.
            total_matches: Initial number of matches.
            parent: Parent Tkinter window.
        """
        self.model = GameModel(total_matches, p1, p2)
        self.view = GameView(parent, self)

    def _bind_buttons(self) -> None:
        """
        Connect action buttons to human moves.
        """
        self.view.btn1.config(command=lambda: self.handle_human_move(1))
        self.view.btn2.config(command=lambda: self.handle_human_move(2))
        self.view.btn3.config(command=lambda: self.handle_human_move(3))

    def start(self) -> None:
        """
        Prepare the game window and start the first turn.
        """
        self.view.reset()
        self._bind_buttons()
        self.view.update_view()
        self._play_ai_turn_if_needed()

    def get_nb_matches(self) -> int:
        """
        Return the number of matches remaining.
        """
        return self.model.nb

    def get_status_message(self) -> str:
        """
        Return the message displayed by the view.
        """
        if not self.model.is_game_over():
            current_player = self.model.get_current_player()
            return (
                f"Current turn: {current_player.name} | "
                f"Matches remaining: {self.model.nb}"
            )

        winner = self.model.get_winner()
        return f"Game over — winner: {winner.name}"

    def reset_game(self) -> None:
        """
        Start a new game with the same players and initial number of matches.
        """
        self.model.reset()
        self.view.reset()
        self._bind_buttons()
        self.view.update_view()
        self._play_ai_turn_if_needed()

    def handle_human_move(self, nb_taken: int) -> None:
        """
        Apply a move selected by the human player.

        Args:
            nb_taken: Number of matches selected from the GUI button.
        """
        current_player = self.model.get_current_player()

        if not isinstance(current_player, HumanGUI):
            return

        self._apply_move(nb_taken)

        if not self.model.is_game_over():
            self._play_ai_turn_if_needed(delay=True)

    def handle_ai_move(self) -> None:
        """
        Let the non-human player choose and apply a move.
        """
        current_player = self.model.get_current_player()

        if isinstance(current_player, HumanGUI):
            return

        max_take = min(3, self.model.nb)
        action = current_player.play(max_take)

        self._apply_move(action)

    def _apply_move(self, action: int) -> None:
        """
        Apply a move, then either end the game or switch player.
        """
        self.model.step(action)

        if self.model.is_game_over():
            self.handle_end_game()
            return

        self.model.switch_player()
        self.view.update_view()

    def _play_ai_turn_if_needed(self, delay: bool = False) -> None:
        """
        Trigger an AI move if the current player is not a GUI human.
        """
        if isinstance(self.model.get_current_player(), HumanGUI):
            return

        if delay:
            self.view.after(self.AI_MOVE_DELAY_MS, self.handle_ai_move)
        else:
            self.handle_ai_move()

    def train_ai_players(self) -> None:
        """
        Train and save AI players after a completed GUI game.

        This lets the AI learn from games played against a human. The updated
        value function is saved so the progress persists after closing the app.
        """
        for player in self.model.players:
            if isinstance(player, AI):
                player.train()
                player.save(self.AI_TRAINING_FILE)

    def handle_end_game(self) -> None:
        """
        Finish the game, update statistics, train AI players, and update the UI.
        """
        winner = self.model.get_winner()
        loser = self.model.get_loser()

        winner.win()
        loser.lose()

        self.train_ai_players()

        self.view.update_view()
        self.view.end_game()

    def show_stats(self) -> None:
        """
        Display cumulative player statistics and close the game window.
        """
        p1, p2 = self.model.players
        stats = f"Game statistics\n\n{p1}\n\n{p2}"
        mb.showinfo("Statistics", stats)
        self.view.destroy()