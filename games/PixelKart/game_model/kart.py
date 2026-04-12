
from dataclasses import dataclass
from games.PixelKart.game_model.types import Position
from games.PixelKart.game_model.direction import Direction

@dataclass(slots=True)
class Kart:
    """State of the kart."""

    position: Position
    direction: Direction
    name: str = "Player"
    color: str = "#f97316"
    pixels_per_turn: int = 0
    laps_completed: int = 0
    turns_elapsed: int = 0
    has_won: bool = False
    has_lost: bool = False
    finish_time: int | None = None

    @property
    def speed(self) -> int:
        """Derived speed expressed in pixels per turn."""
        return self.pixels_per_turn

    @property
    def is_active(self) -> bool:
        return not (self.has_won or self.has_lost)

    def reset(self, position: Position) -> None:
        """Reset this kart to a start-line position."""
        self.position = position
        self.direction = Direction.EAST
        self.pixels_per_turn = 0
        self.laps_completed = 0
        self.turns_elapsed = 0
        self.has_won = False
        self.has_lost = False
        self.finish_time = None