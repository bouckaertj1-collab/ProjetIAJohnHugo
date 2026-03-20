import random


class Player:
    """Base class for a Cubee player."""

    def __init__(self, name: str, position: tuple[int, int],) -> None:
        """
        Initialize a player.

        Args:
            name: The player name.
            position: The current player position on the board.
        """
        self.name = name
        self.position = position

        self.nb_win: int = 0
        self.nb_lose: int = 0
        self.nb_draw: int = 0
        self.nb_game: int = 0

    def is_ai(self) -> bool:
        """
        Tell whether this player is controlled by the AI.

        Returns:
            False for a regular player.
        """
        return False

    def play(self, game_model) -> str | None:
        """
        Return the move to play.

        Args:
            game_model: The current game model.

        Returns:
            The chosen move, or None if no move is available.
        """
        return None

    def win(self) -> None:
        """Record a win for this player."""
        self.nb_win += 1
        self.nb_game += 1

    def lose(self) -> None:
        """Record a loss for this player."""
        self.nb_lose += 1
        self.nb_game += 1

    def draw(self) -> None:
        """Record a draw for this player."""
        self.nb_draw += 1
        self.nb_game += 1

class RandomAgent(Player):
    """Very simple AI that plays a random move."""

    def is_ai(self) -> bool:
        """
        Tell whether this player is controlled by the AI.

        Returns:
            True for this AI player.
        """
        return True

    def play(self, game_model) -> str | None:
        """
        Choose and return a random legal move.

        Args:
            game_model: The current game model.

        Returns:
            A random move, or None if no move is available.
        """
        moves = game_model.available_moves()
        if not moves:
            return None
        return random.choice(moves)