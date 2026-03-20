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
    
    def is_ai(self) -> bool:
        """
        Tell whether this player is controlled by the AI.

        Returns:
            False for a regular player.
        """
        return False


class RandomAgent(Player):
    """Very simple AI that plays a random move."""

    def is_ai(self) -> bool:
        """
        Tell whether this player is controlled by the AI.

        Returns:
            True for this AI player.
        """
        return True

    def play(self, game_model) -> str:
        """
        Choose and return a random legal move.

        Args:
            game_model: The current game model.

        Returns:
            A random legal move.
        """
        moves = game_model.available_moves()
        return random.choice(moves)