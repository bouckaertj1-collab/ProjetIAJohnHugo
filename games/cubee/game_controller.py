from games.cubee.game_model import GameModel
from games.cubee.game_view import GameView
from games.cubee.player import QLearningAgent

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
        Apply a player move.

        Args:
            move: The move to play.

        Returns:
            True if the move was handled, False if it failed.
        """
        success = self.model.step(move)

        self._update_view()

        if not success:
            return False

        if self.model.is_game_over:
            self.handle_end_game()
            return True

        self.handle_ai_move()
        return True

    def handle_ai_move(self) -> bool:
        """
        Let the AI play if it is the current player's turn.

        Returns:
            True if an AI move was played successfully, False otherwise.
        """
        current_player = self.model.current_player

        if not current_player.is_ai():
            return False

        old_score = self.model.score
        move = current_player.play(self.model)
        success = self.model.step(move)

        if success and isinstance(current_player, QLearningAgent):
            new_state = current_player.get_state_key(self.model)
            new_legal_moves = self.model.available_moves() if not self.model.is_game_over else []
            reward = current_player.compute_reward(old_score, self.model.score, self.model)
            current_player.learn(reward, new_state, new_legal_moves, self.model.is_game_over)

        self._update_view()

        if success and self.model.is_game_over:
            self.handle_end_game()

        return success

    def handle_cell_click(self, row: int, col: int) -> bool:
        """
        Handle a click on a board cell.

        The clicked cell is converted into a move if it is adjacent
        to the current player's position.

        Args:
            row: Clicked row.
            col: Clicked column.

        Returns:
            True if the click produced a valid move, False otherwise.
        """
        state = self.get_state_DTO()

        if state["turn"] == 1:
            current_row, current_col = state["pos_p1"]
        else:
            current_row, current_col = state["pos_p2"]

        moves = {
            (-1, 0): "up",
            (1, 0): "down",
            (0, -1): "left",
            (0, 1): "right",
        }

        move = moves.get((row - current_row, col - current_col))
        if move is None:
            return False

        return self.handle_move(move)

    def handle_end_game(self) -> None:
        """Notify the view that the game is over."""
        for player in [self.model.player1, self.model.player2]:
            if isinstance(player, QLearningAgent):
                player.upload("games/cubee/cubee_qtable.json")
                player.next_epsilon()
                player.reset_memory()   
                     
        if self.view is not None:
            self.view.end_game(
                self.get_status_message(),
                self.get_state_DTO(),
            )

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
        """
        Return the current game state.

        Returns:
            The current game state as a dictionary.
        """
        return self.model.get_state_DTO()
    
