from __future__ import annotations

import random

from games.pixelKart.model.dto import KartDTO
from games.pixelKart.model.movement import Action, Direction


class Kart:
    """Represents a kart participating in a race."""

    MIN_SPEED = -1
    MAX_SPEED = 2

    def __init__(
        self,
        name: str,
        color: str,
        position: tuple[int, int],
        direction: Direction = Direction.EAST,
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

    def apply_action(self, action: Action) -> None:
        """
        Apply an action to the kart state.

        Args:
            action: Action chosen for this turn.
        """
        if action == Action.ACCELERATE:
            self.speed = min(self.speed + 1, self.MAX_SPEED)
        elif action == Action.BRAKE:
            self.speed = max(self.speed - 1, self.MIN_SPEED)
        elif action == Action.TURN_LEFT:
            self.direction = self.direction.turn_left()
        elif action == Action.TURN_RIGHT:
            self.direction = self.direction.turn_right()

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
            direction=self.direction.name,
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

    def choose_action(self) -> Action:
        """
        Choose a random action among all available actions.

        Returns:
            A randomly selected action.
        """
        return random.choice(list(Action))