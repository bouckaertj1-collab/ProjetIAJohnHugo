from __future__ import annotations

from typing import TypedDict


class CircuitDTO(TypedDict):
    name: str
    grid: str


class KartDTO(TypedDict):
    name: str
    color: str
    position: tuple[int, int]
    direction: str
    speed: int
    laps_done: int
    is_ai: bool
    is_alive: bool
    has_finished: bool


class RaceDTO(TypedDict):
    time: int
    total_laps: int
    current_player_index: int
    finished: bool
    winner_name: str | None