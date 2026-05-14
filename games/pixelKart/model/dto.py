from __future__ import annotations

from typing import TypedDict


class CircuitDTO(TypedDict):
    """
    Data transfer object representing a circuit.

    A DTO is used to expose model data without giving direct access to the
    model object itself.

    Attributes:
        name: Display name of the circuit.
        grid: Text representation of the circuit layout.
    """

    name: str
    grid: str


class KartDTO(TypedDict):
    """
    Data transfer object representing the public state of a kart.

    This structure is mainly used by the view/controller layer to display the
    kart without directly depending on the Kart object.

    Attributes:
        name: Kart name displayed to the user.
        color: Kart color used by the graphical view.
        position: Current row and column of the kart on the circuit grid.
        direction: Current direction of the kart, such as NORTH or EAST.
        speed: Current speed of the kart.
        laps_done: Number of completed laps.
        is_ai: True when the kart is controlled by an AI.
        is_alive: False when the kart has crashed.
        has_finished: True when the kart has completed the race.
    """

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
    """
    Data transfer object representing the public state of a race.

    This DTO gives the controller and the view the information needed to update
    the interface without exposing the full Race object.

    Attributes:
        time: Number of turns played since the beginning of the race.
        total_laps: Number of laps required to finish the race.
        current_player_index: Index of the kart whose turn is currently active.
        finished: True when the race is over.
        winner_name: Name of the winning kart, or None if there is no winner yet.
    """

    time: int
    total_laps: int
    current_player_index: int
    finished: bool
    winner_name: str | None