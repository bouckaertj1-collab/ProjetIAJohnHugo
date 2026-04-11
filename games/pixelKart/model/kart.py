from __future__ import annotations

import random

from games.pixelKart.model.dto import KartDTO


class Kart:
    """Represents a kart participating in a race."""

    MIN_SPEED = -1
    MAX_SPEED = 2

    def __init__(
        self,
        name: str,
        color: str,
        position: tuple[int, int],
        direction: str = "EAST",
        speed: int = 0,
        laps_done: int = 0,
        is_alive: bool = True,
    ) -> None:
        """
        Initialize a kart.

        Args:
            name: Kart name.
            color: Display color used by the view.
            position: Current kart position as (row, col).
            direction: Current facing direction.
            speed: Current speed.
            laps_done: Number of completed laps.
            is_alive: Whether the kart is still in the race.
        """
        self.name = name
        self.color = color
        self.position = position
        self.direction = direction
        self.speed = max(self.MIN_SPEED, min(self.MAX_SPEED, speed))
        self.laps_done = laps_done
        self.is_alive = is_alive

    @property
    def is_ai(self) -> bool:
        """Return whether the kart is controlled by an AI."""
        return False

    def turn_left(self) -> None:
        """Turn the kart 90 degrees to the left."""
        if self.direction == "NORTH":
            self.direction = "WEST"
        elif self.direction == "WEST":
            self.direction = "SOUTH"
        elif self.direction == "SOUTH":
            self.direction = "EAST"
        else:
            self.direction = "NORTH"

    def turn_right(self) -> None:
        """Turn the kart 90 degrees to the right."""
        if self.direction == "NORTH":
            self.direction = "EAST"
        elif self.direction == "EAST":
            self.direction = "SOUTH"
        elif self.direction == "SOUTH":
            self.direction = "WEST"
        else:
            self.direction = "NORTH"

    def opposite_direction(self) -> str:
        """Return the opposite of the current direction."""
        if self.direction == "NORTH":
            return "SOUTH"
        if self.direction == "SOUTH":
            return "NORTH"
        if self.direction == "EAST":
            return "WEST"
        return "EAST"

    def direction_to_vector(self, direction: str | None = None) -> tuple[int, int]:
        """
        Convert a direction to a movement vector.

        Args:
            direction: Direction to convert. If None, use the current kart direction.

        Returns:
            A movement vector as (row_step, col_step).
        """
        target_direction = self.direction if direction is None else direction

        if target_direction == "NORTH":
            return -1, 0
        if target_direction == "EAST":
            return 0, 1
        if target_direction == "SOUTH":
            return 1, 0
        return 0, -1

    def apply_action(self, action: str) -> None:
        """
        Apply an action to the kart state.

        Args:
            action: Action chosen for this turn.
        """
        if action == "accelerate":
            self.speed = min(self.speed + 1, self.MAX_SPEED)
        elif action == "brake":
            self.speed = max(self.speed - 1, self.MIN_SPEED)
        elif action == "turn_left":
            self.turn_left()
        elif action == "turn_right":
            self.turn_right()

    def reset_speed(self) -> None:
        """Reset the kart speed to zero."""
        self.speed = 0

    def complete_lap(self) -> None:
        """Increase the number of completed laps by one."""
        self.laps_done += 1

    def eliminate(self) -> None:
        """Mark the kart as eliminated."""
        self.is_alive = False

    def to_dto(self) -> KartDTO:
        """
        Convert the kart to a data transfer object.

        Returns:
            A KartDTO representing the current kart state.
        """
        return KartDTO(
            name=self.name,
            color=self.color,
            position=self.position,
            direction=self.direction,
            speed=self.speed,
            laps_done=self.laps_done,
            is_ai=self.is_ai,
            is_alive=self.is_alive,
        )


class HumanKart(Kart):
    """Represents a human-controlled kart."""


class RandomAIKart(Kart):
    """Represents a kart controlled by a random AI."""

    @property
    def is_ai(self) -> bool:
        """Return True because this kart is AI-controlled."""
        return True

    def choose_action(self) -> str:
        """
        Choose a random action among all available actions.

        Returns:
            A randomly selected action.
        """
        return random.choice(
            ["accelerate", "brake", "turn_left", "turn_right", "pass"]
        )