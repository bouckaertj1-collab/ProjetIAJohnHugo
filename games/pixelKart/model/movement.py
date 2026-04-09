from __future__ import annotations

from enum import Enum


class Direction(Enum):
    """Represent the four possible directions of a kart."""

    NORTH = (-1, 0)
    EAST = (0, 1)
    SOUTH = (1, 0)
    WEST = (0, -1)

    def turn_left(self) -> "Direction":
        """Return the direction after a 90-degree left turn."""
        if self == Direction.NORTH:
            return Direction.WEST
        if self == Direction.WEST:
            return Direction.SOUTH
        if self == Direction.SOUTH:
            return Direction.EAST
        return Direction.NORTH

    def turn_right(self) -> "Direction":
        """Return the direction after a 90-degree right turn."""
        if self == Direction.NORTH:
            return Direction.EAST
        if self == Direction.EAST:
            return Direction.SOUTH
        if self == Direction.SOUTH:
            return Direction.WEST
        return Direction.NORTH

    def opposite(self) -> "Direction":
        """Return the opposite direction."""
        if self == Direction.NORTH:
            return Direction.SOUTH
        if self == Direction.SOUTH:
            return Direction.NORTH
        if self == Direction.EAST:
            return Direction.WEST
        return Direction.EAST

    def to_vector(self) -> tuple[int, int]:
        """Return the movement vector of the direction."""
        return self.value


class Action(Enum):
    """Represent all possible actions of a kart."""

    ACCELERATE = "accelerate"
    BRAKE = "brake"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    PASS = "pass"