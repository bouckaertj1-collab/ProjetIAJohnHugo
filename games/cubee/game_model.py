import random
from collections import deque

try:
    from games.cubee.player import Player
except ModuleNotFoundError:
    from player import Player


class GameModel:
    """Main model for the Cubee game."""

    MOVES: dict[str, tuple[int, int]] = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    def __init__(self, player1: Player | str, player2: Player | str, size: int = 5) -> None:
        """
        Initialize the game model.

        Args:
            player1: The first player or the player name.
            player2: The second player or the player name.
            size: The board size.
        """
        self.size = size

        self.player1 = player1 if isinstance(player1, Player) else Player(player1, (0, 0))
        self.player2 = player2 if isinstance(player2, Player) else Player(player2, (size - 1, size - 1))

        self.board: list[list[int]] = []
        self.is_game_over = False
        self.player_turn = 1
        self.winner: Player | None = None
        self.loser: Player | None = None
        self.score: tuple[int, int] = (0, 0)

        self.reset()

    @property
    def current_player(self) -> Player:
        """Return the player whose turn it is."""
        return self.player1 if self.player_turn == 1 else self.player2

    def reset(self) -> None:
        """Reset the game to its initial state."""
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]

        self.player1.position = (0, 0)
        self.player2.position = (self.size - 1, self.size - 1)

        self.board[0][0] = 1
        self.board[self.size - 1][self.size - 1] = 2

        self.is_game_over = False
        self.player_turn = random.choice([1, 2])
        self.winner = None
        self.loser = None

        self.update_score()

    def get_opponent(self, player: Player | None = None) -> Player:
        """
        Return the opponent of the given player.

        Args:
            player: The reference player. If None, use the current player.

        Returns:
            The other player.
        """
        if player is None:
            player = self.current_player
        return self.player2 if player == self.player1 else self.player1

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        """
        Check if a position is inside the board.

        Args:
            position: The position to check.

        Returns:
            True if the position is inside the board, False otherwise.
        """
        row, col = position
        return 0 <= row < self.size and 0 <= col < self.size

    def get_target_position(self, move: str) -> tuple[int, int]:
        """
        Return the target position for a move.

        Args:
            move: The move to apply.

        Returns:
            The new position after the move.
        """
        row, col = self.current_player.position
        d_row, d_col = self.MOVES[move]
        return row + d_row, col + d_col

    def is_legal_move(self, move: str) -> bool:
        """
        Check whether a move is legal.

        A player can move:
        - to an empty cell
        - to a cell they already own

        A player cannot move:
        - outside the board
        - to an opponent cell

        Args:
            move: The move to check.

        Returns:
            True if the move is legal, False otherwise.
        """
        player = self.current_player
        row, col = self.get_target_position(move)

        if not self.is_in_bounds((row, col)):
            return False

        target_cell = self.board[row][col]
        opponent_value = 2 if player == self.player1 else 1

        return target_cell != opponent_value

    def available_moves(self) -> list[str]:
        """
        Return the list of legal moves for the current player.

        Returns:
            A list of move names.
        """
        return [move for move in self.MOVES if self.is_legal_move(move)]

    def next_player(self) -> None:
        """Switch to the other player."""
        self.player_turn = 2 if self.player_turn == 1 else 1

    def update_score(self) -> None:
        """Recompute the score from the board."""
        flat_board = [cell for row in self.board for cell in row]
        self.score = (flat_board.count(1), flat_board.count(2))

    def end_game(self) -> None:
        """End the game and update player statistics."""
        self.is_game_over = True

        if self.score[0] > self.score[1]:
            self.winner = self.player1
            self.loser = self.player2
            self.player1.win()
            self.player2.lose()
        elif self.score[1] > self.score[0]:
            self.winner = self.player2
            self.loser = self.player1
            self.player2.win()
            self.player1.lose()
        else:
            self.winner = None
            self.loser = None
            self.player1.draw()
            self.player2.draw()

    def check_game_over(self) -> bool:
        """
        Check whether the game is over.

        Returns:
            True if the game is over, False otherwise.
        """
        if not any(0 in row for row in self.board):
            self.end_game()
            return True
        return False

    def check_enclosure(self) -> None:
        """
        Fill enclosed empty cells with the current player's value.

        This method uses a breadth-first search from the opponent position
        to find all cells the opponent can still reach.
        """
        opponent = self.get_opponent(self.current_player)

        current_value = self.player_turn
        opponent_value = 2 if current_value == 1 else 1

        reachable = [[False for _ in range(self.size)] for _ in range(self.size)]
        queue = deque([opponent.position])

        start_row, start_col = opponent.position
        reachable[start_row][start_col] = True

        while queue:
            row, col = queue.popleft()

            for d_row, d_col in self.MOVES.values():
                new_row, new_col = row + d_row, col + d_col

                if not self.is_in_bounds((new_row, new_col)):
                    continue

                if reachable[new_row][new_col]:
                    continue

                if self.board[new_row][new_col] in (0, opponent_value):
                    reachable[new_row][new_col] = True
                    queue.append((new_row, new_col))

        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0 and not reachable[row][col]:
                    self.board[row][col] = current_value

    def step(self, move: str) -> bool:
        """
        Apply one move for the current player.

        Args:
            move: The move to play.

        Returns:
            True if the move was applied, False otherwise.
        """
        if self.is_game_over:
            return False

        if not self.is_legal_move(move):
            return False

        new_row, new_col = self.get_target_position(move)

        self.current_player.position = (new_row, new_col)
        self.board[new_row][new_col] = self.player_turn

        self.check_enclosure()
        self.update_score()

        if not self.check_game_over():
            self.next_player()

        return True

    def board_to_string(self) -> str:
        """
        Convert the board into a compact string.

        Returns:
            The board as a single string.
        """
        return "".join(str(cell) for row in self.board for cell in row)

    def get_state_DTO(self) -> dict:
        """
        Return the current game state as a dictionary.

        Returns:
            A dictionary with the current game state.
        """
        return {
            "size": self.size,
            "board": self.board_to_string(),
            "turn": self.player_turn,
            "pos_p1": self.player1.position,
            "pos_p2": self.player2.position,
            "is_game_over": self.is_game_over,
            "score": self.score,
            "winner": self.winner.name if self.winner else None,
            "loser": self.loser.name if self.loser else None,
        }