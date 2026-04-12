
from enum import StrEnum

class Direction(StrEnum):
    """Cardinal directions used by the kart."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    @property
    def delta(self) -> tuple[int, int]:
        """Return the row/column delta for one step in this direction."""
        mapping = {
            Direction.NORTH: (-1, 0),
            Direction.SOUTH: (1, 0),
            Direction.EAST: (0, 1),
            Direction.WEST: (0, -1),
        }
        return mapping[self]

    def turn_left(self) -> "Direction":
        """Return the direction after a 90-degree left turn."""
        mapping = {
            Direction.NORTH: Direction.WEST,
            Direction.WEST: Direction.SOUTH,
            Direction.SOUTH: Direction.EAST,
            Direction.EAST: Direction.NORTH,
        }
        return mapping[self]

    def turn_right(self) -> "Direction":
        """Return the direction after a 90-degree right turn."""
        mapping = {
            Direction.NORTH: Direction.EAST,
            Direction.EAST: Direction.SOUTH,
            Direction.SOUTH: Direction.WEST,
            Direction.WEST: Direction.NORTH,
        }
        return mapping[self]

    def opposite(self) -> "Direction":
        """Return the opposite direction."""
        mapping = {
            Direction.NORTH: Direction.SOUTH,
            Direction.SOUTH: Direction.NORTH,
            Direction.EAST: Direction.WEST,
            Direction.WEST: Direction.EAST,
        }
        return mapping[self]