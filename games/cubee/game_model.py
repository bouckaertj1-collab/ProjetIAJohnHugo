import random
from collections import deque

from games.cubee.player import Player


class GameModel:
    """Main model for the Cubee game."""

    MOVES: dict[str, tuple[int, int]] = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }

    def __init__(self, player1: Player, player2: Player, size: int = 5) -> None:
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

        self.player1.game_model = self
        self.player2.game_model = self

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

    def get_start_positions(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Return the starting positions for player1 and player2.

        The starting corners alternate every game to avoid training the AI
        only from one initial configuration.
        """
        corner1 = (0, 0)
        corner2 = (self.size - 1, self.size - 1)
        return (corner1, corner2) if self.player1.nb_game % 2 == 0 else (corner2, corner1)

    def reset(self) -> None:
        """Reset the game to its initial state."""
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]

        p1_pos, p2_pos = self.get_start_positions()
        self.player1.position = p1_pos
        self.player2.position = p2_pos

        self.board[p1_pos[0]][p1_pos[1]] = 1
        self.board[p2_pos[0]][p2_pos[1]] = 2

        self.is_game_over = False
        self.player_turn = random.choice([1, 2])
        self.winner = None
        self.loser = None

        self.update_score()

    def is_in_bounds(self, position: tuple[int, int]) -> bool:
        """Check if a position is inside the board."""
        row, col = position
        return 0 <= row < self.size and 0 <= col < self.size

    def get_target_position_for(self, player: Player, move: str) -> tuple[int, int]:
        """Return the target position for a move played by a specific player."""
        row, col = player.position
        d_row, d_col = self.MOVES[move]
        return row + d_row, col + d_col

    def get_target_position(self, move: str) -> tuple[int, int]:
        """Return the target position for the current player."""
        return self.get_target_position_for(self.current_player, move)

    def is_legal_move_for(self, player: Player, move: str) -> bool:
        """
        Check whether a move is legal for a specific player.

        A player can move:
        - to an empty cell
        - to a cell they already own

        A player cannot move:
        - outside the board
        - to an opponent cell
        """
        row, col = self.get_target_position_for(player, move)
        if not self.is_in_bounds((row, col)):
            return False

        target_cell = self.board[row][col]
        opponent_value = 2 if player == self.player1 else 1
        return target_cell != opponent_value

    def is_legal_move(self, move: str) -> bool:
        """Check whether a move is legal for the current player."""
        return self.is_legal_move_for(self.current_player, move)

    def available_moves_for(self, player: Player) -> list[str]:
        """Return the list of legal moves for a specific player."""
        return [move for move in self.MOVES if self.is_legal_move_for(player, move)]

    def available_moves(self) -> list[str]:
        """Return the list of legal moves for the current player."""
        return self.available_moves_for(self.current_player)

    def next_player(self) -> None:
        """Switch to the other player."""
        self.player_turn = 3 - self.player_turn

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

        self.player1.on_game_over()
        self.player2.on_game_over()

    def check_enclosure(self) -> None:
        """
        Fill enclosed empty cells with the current player's value.

        This method uses a breadth-first search from the opponent position
        to find all cells the opponent can still reach.
        """
        opponent = self.player2 if self.player_turn == 1 else self.player1
        current_value = self.player_turn
        opponent_value = 2 if opponent == self.player2 else 1

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
        if self.is_game_over or not self.is_legal_move(move):
            return False

        new_row, new_col = self.get_target_position(move)

        self.current_player.position = (new_row, new_col)
        self.board[new_row][new_col] = self.player_turn

        self.check_enclosure()
        self.update_score()

        if not any(0 in row for row in self.board):
            self.end_game()
        else:
            self.next_player()

        return True

    def board_to_string(self) -> str:
        """Convert the board into a compact string."""
        return "".join(str(cell) for row in self.board for cell in row)

    def get_state_DTO(self) -> dict:
        """Return the current game state as a dictionary."""
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
