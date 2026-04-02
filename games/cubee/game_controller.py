from typing import TYPE_CHECKING

from games.cubee.player import QLearningAgent, RandomAgent

if TYPE_CHECKING:
    from games.cubee.game_model import GameModel
    from games.cubee.game_view import GameView


class GameController:
    """Main controller for the Cubee game."""

    def __init__(self, model: "GameModel", view: "GameView | None" = None) -> None:
        """
        Initialize the controller.

        Args:
            model: The game model.
            view: The game view. Can be None.
        """
        self.model = model
        self.view = view

    def _update_view(self) -> None:
        """Refresh the view if a view is attached."""
        if self.view is not None:
            self.view.update_view(self.get_state_DTO())

    def start(self) -> None:
        """Start the game and refresh the view."""
        self._update_view()
        self.handle_ai_move()

    def reset(self) -> None:
        """Reset the game and refresh the view."""
        self.model.reset()
        self.start()

    def handle_move(self, move: str) -> bool:
        """
        Apply a human move.

        Args:
            move: The move to play.

        Returns:
            True if the move was handled, False otherwise.
        """
        success = self.model.step(move)
        if not success:
            return False

        self._update_view()

        if self.model.is_game_over:
            self.handle_end_game()
        else:
            self.handle_ai_move()

        return True

    def handle_ai_move(self) -> bool:
        """
        Let AI players play until it is no longer their turn.

        Returns:
            True if at least one AI move was played, False otherwise.
        """
        has_played = False

        while not self.model.is_game_over and isinstance(
            self.model.current_player,
            (QLearningAgent, RandomAgent),
        ):
            success = self.model.current_player.play()
            if not success:
                return has_played

            has_played = True
            self._update_view()

        if self.model.is_game_over:
            self.handle_end_game()

        return has_played

    def handle_cell_click(self, row: int, col: int) -> bool:
        """
        Handle a click on a board cell.

        The clicked cell is converted into a move if it is adjacent
        to the current player's position.
        """
        state = self.get_state_DTO()
        current_row, current_col = state["pos_p1"] if state["turn"] == 1 else state["pos_p2"]

        moves = {
            (-1, 0): "up",
            (1, 0): "down",
            (0, -1): "left",
            (0, 1): "right",
        }

        move = moves.get((row - current_row, col - current_col))
        if not move:
            return False

        return self.handle_move(move)

    def handle_end_game(self) -> None:
        """Process the end of the game."""
        final_state = self.get_state_DTO()
        message = self.get_status_message()

        if self.view is not None:
            self.view.end_game(message, final_state)

    def get_status_message(self) -> str:
        """
        Build the current game status message.

        Returns:
            A message with the game result or current turn, followed by
            player statistics.
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
        """Return the current game state."""
        return self.model.get_state_DTO()
