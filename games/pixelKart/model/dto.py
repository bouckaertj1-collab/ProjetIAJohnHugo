from __future__ import annotations


class CircuitDTO:
    """Store serialized circuit data."""

    def __init__(self, name: str, grid: str) -> None:
        self.name = name
        self.grid = grid


class KartDTO:
    """Store the current state of a kart."""

    def __init__(
        self,
        name: str,
        color: str,
        position: tuple[int, int],
        direction: str,
        speed: int,
        laps_done: int,
        is_ai: bool,
        is_alive: bool,
    ) -> None:
        self.name = name
        self.color = color
        self.position = position
        self.direction = direction
        self.speed = speed
        self.laps_done = laps_done
        self.is_ai = is_ai
        self.is_alive = is_alive


class RaceDTO:
    """Store the current state of a race."""

    def __init__(
        self,
        time: int,
        total_laps: int,
        current_player_index: int,
        finished: bool,
        winner_name: str | None,
    ) -> None:
        self.time = time
        self.total_laps = total_laps
        self.current_player_index = current_player_index
        self.finished = finished
        self.winner_name = winner_name