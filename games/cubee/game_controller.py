from typing import TYPE_CHECKING

from games.cubee.player import QLearningAgent, RandomAgent

if TYPE_CHECKING:
    from games.cubee.game_model import GameModel
    from games.cubee.game_view import GameView


class GameController:
    """
    Controller for the Cubee game.

    The controller connects the graphical interface to the game model.
    It converts user interactions into model actions, lets AI players play
    automatically, refreshes the view, and displays the final result.
    """

    AI_PLAYER_TYPES = (QLearningAgent, RandomAgent)

    CELL_TO_MOVE = {
        (-1, 0): "up",
        (1, 0): "down",
        (0, -1): "left",
        (0, 1): "right",
    }

    def __init__(self, model: "GameModel", view: "GameView | None" = None) -> None:
        """
        Initialize the controller.

        Args:
            model: The Cubee game model controlled by this object.
            view: The graphical view attached to the controller.
                It can be None during initialization or tests.
        """
        self.model = model
        self.view = view

    def _update_view(self) -> None:
        """
        Refresh the graphical view.

        The view can be missing during initialization or tests, so the controller
        only updates it when it is attached.
        """
        if self.view is not None:
            self.view.update_view(self.get_state_DTO())

    def start(self) -> None:
        """
        Start or resume the game display.

        The view is refreshed first. If the first player is an AI, the controller
        immediately lets the AI play until a human player has to act or the game ends.
        """
        self._update_view()
        self.handle_ai_move()

    def reset(self) -> None:
        """
        Reset the model and restart the controller flow.

        After the reset, the board is refreshed and AI players are allowed to play
        automatically if the first turn belongs to an AI.
        """
        self.model.reset()
        self.start()

    def handle_move(self, move: str) -> bool:
        """
        Apply a human move to the model.

        Args:
            move: Direction chosen by the human player.

        Returns:
            True if the move was accepted by the model, False if the move was illegal.
        """
        if not self.model.step(move):
            return False

        self._update_view()

        if self.model.is_game_over:
            self.handle_end_game()
        else:
            self.handle_ai_move()

        return True

    def handle_ai_move(self) -> None:
        """
        Let AI players play automatically.

        The loop continues while the current player is an AI and the game is not over.
        Move validation and game-over detection stay in the model/player layer; the
        controller only triggers AI turns and refreshes the view after each move.
        """
        while (
            not self.model.is_game_over
            and isinstance(self.model.current_player, self.AI_PLAYER_TYPES)
        ):
            self.model.current_player.play()
            self._update_view()

        if self.model.is_game_over:
            self.handle_end_game()

    def handle_cell_click(self, row: int, col: int) -> bool:
        """
        Convert a clicked board cell into a move.

        Only adjacent cells correspond to valid movement directions. A click on a
        non-adjacent cell is ignored and returns False.
        """
        state = self.get_state_DTO()
        current_row, current_col = state["pos_p1"] if state["turn"] == 1 else state["pos_p2"]

        row_delta = row - current_row
        col_delta = col - current_col

        move = self.CELL_TO_MOVE.get((row_delta, col_delta))

        if move is None:
            return False

        return self.handle_move(move)

    def handle_end_game(self) -> None:
        """
        Display the final result when the game is over.

        The model is responsible for computing the winner, the score, and player
        statistics. The controller only prepares the final message and sends it
        to the view.
        """
        if self.view is not None:
            self.view.end_game(self.get_status_message(), self.get_state_DTO())

    def get_status_message(self) -> str:
        """
        Build the current game status message.

        Returns:
            A message containing either the current turn or the final result,
            followed by both players' statistics.
        """
        p1 = self.model.player1
        p2 = self.model.player2

        if self.model.is_game_over:
            if self.model.winner is None:
                result = f"Draw: {self.model.score[0]} - {self.model.score[1]}"
            else:
                result = (
                    f"{self.model.winner.name} wins: "
                    f"{self.model.score[0]} - {self.model.score[1]}"
                )
        else:
            result = f"Player {self.model.player_turn}'s turn"

        stats = (
            f"\n\n{p1.name} - Games: {p1.nb_game}, W: {p1.nb_win}, "
            f"L: {p1.nb_lose}, D: {p1.nb_draw}"
            f"\n{p2.name} - Games: {p2.nb_game}, W: {p2.nb_win}, "
            f"L: {p2.nb_lose}, D: {p2.nb_draw}"
        )

        return result + stats

    def get_state_DTO(self) -> dict:
        """
        Return the current game state as a DTO.

        The DTO is produced by the model and used by the view to render the board.
        """
        return self.model.get_state_DTO()