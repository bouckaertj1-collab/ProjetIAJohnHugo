"""
Controller for the matches game (MVC).

Responsibilities:
    - Link GUI actions to game logic
    - Update the game state and refresh the GUI
    - Trigger AI moves when it's not the human's turn
"""

from model.human import HumanGUI
from model.player import Player
from model.game_model import GameModel
from view.game_view import GameView


class GameController:
    """
    Connects the GameModel and GameView.

    This controller also manages turn switching and end-of-game handling.
    """

    def __init__(self, p1: Player, p2: Player, total_matches: int) -> None:
        """
        Initialize controller, model, and view.

        Args:
            p1: First player.
            p2: Second player.
            total_matches: Initial number of matches.

        Raises:
            ValueError: If there is no HumanGUI player (GUI requires at least one).
        """
        if not isinstance(p1, HumanGUI) and not isinstance(p2, HumanGUI):
            raise ValueError("GUI requires at least one human player (HumanGUI).")

        self.model = GameModel(total_matches, p1, p2)
        self.view = GameView(self)

        self._bind_buttons()

        # If AI starts, trigger it immediately
        if not isinstance(self.model.get_current_player(), HumanGUI):
            self.handle_ai_move()

    def _bind_buttons(self) -> None:
        """
        Bind GUI buttons to controller actions.

        Postconditions:
            - Buttons (1/2/3) trigger handle_human_move with the correct value.
        """
        self.view.btn1.config(command=lambda: self.handle_human_move(1))
        self.view.btn2.config(command=lambda: self.handle_human_move(2))
        self.view.btn3.config(command=lambda: self.handle_human_move(3))

    def start(self) -> None:
        """
        Start the Tkinter main loop.

        Postconditions:
            - The GUI event loop runs until the window is closed.
        """
        self.view.mainloop()

    def get_nb_matches(self) -> int:
        """
        Provide remaining matches for the view.

        Returns:
            Current number of matches in the model.
        """
        return self.model.nb

    def get_status_message(self) -> str:
        """
        Provide a status message for the view.

        Returns:
            A string describing whose turn it is, or the winner if game is over.
        """
        if not self.model.is_game_over():
            return f"Au tour de : {self.model.get_current_player().name} | Allumettes restantes : {self.model.nb} "
        winner = self.model.get_winner()
        return f"Partie terminée — gagnant : {winner.name}"

    def reset_game(self) -> None:
        """
        Reset the game and restore the default UI.

        Postconditions:
            - model is reset
            - view is reset (buttons recreated)
            - buttons are re-bound
            - if AI starts, it plays
        """
        self.model.reset()
        self.view.reset()
        self._bind_buttons()

        if not isinstance(self.model.get_current_player(), HumanGUI):
            self.handle_ai_move()

        self.view.update_view()

    def handle_human_move(self, nb_taken: int) -> None:
        """
        Handle a human move (button click).

        Args:
            nb_taken: Number of matches requested to take (1..3).

        Preconditions:
            - It must be the human player's turn.

        Postconditions:
            - Applies the move, checks end of game, switches player, updates view.
            - If next player is AI, schedules an AI move.
        """
        current = self.model.get_current_player()

        # Ignore clicks if it's not human's turn
        if not isinstance(current, HumanGUI):
            return

        self.model.step(nb_taken)

        if self.model.is_game_over():
            self.handle_end_game()
            return

        self.model.switch_player()
        self.view.update_view()

        # If AI's turn, play after a short delay
        if not isinstance(self.model.get_current_player(), HumanGUI):
            self.view.after(800, self.handle_ai_move)

    def handle_ai_move(self) -> None:
        """
        Handle an AI move.

        Preconditions:
            - It must be the AI player's turn.

        Postconditions:
            - Applies the AI move, checks end of game, switches player, updates view.
        """
        current = self.model.get_current_player()

        action = current.play()          # expected 1..3
        if action > self.model.nb:       # clamp to remaining matches
            action = self.model.nb

        self.model.step(action)

        if self.model.is_game_over():
            self.handle_end_game()
            return

        self.model.switch_player()
        self.view.update_view()

    def handle_end_game(self) -> None:
        """
        Finalize the game: update stats and switch the UI to end-game mode.

        Postconditions:
            - Winner gains 1 win
            - Loser gains 1 loss
            - View is updated and shows a restart button
        """
        winner = self.model.get_winner()
        loser = self.model.get_loser()

        winner.win()
        loser.lose()

        self.view.update_view()
        self.view.end_game()
