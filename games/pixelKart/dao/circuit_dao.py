from __future__ import annotations

import os

from games.pixelKart.model.dto import CircuitDTO


FILE_PATH = "games/pixelKart/circuits.txt"


def get_all() -> dict[str, str]:
    """
    Retrieve all saved circuits.

    Returns:
        Dictionary mapping each circuit name to its serialized grid.
    """
    circuits: dict[str, str] = {}

    if not os.path.exists(FILE_PATH):
        return circuits

    with open(FILE_PATH, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line or ":" not in line:
                continue

            name, grid = line.split(":", maxsplit=1)
            name = name.strip()
            grid = grid.strip()

            if name and grid:
                circuits[name] = grid

    return circuits

def save_circuit(name: str, grid: str) -> None:
    """
    Save a new circuit.

    Args:
        name: Circuit name.
        grid: Serialized circuit.

    Raises:
        ValueError: If the name or grid is empty, or if the circuit already exists.
    """
    name = name.strip()
    grid = grid.strip()

    if not name:
        raise ValueError("Circuit name cannot be empty.")

    if not grid:
        raise ValueError("Circuit grid cannot be empty.")

    circuits = get_all()

    if name in circuits:
        raise ValueError(f"The circuit '{name}' already exists.")

    circuits[name] = grid
    _write_all(circuits)

def _write_all(circuits: dict[str, str]) -> None:
    """
    Rewrite the circuits file.

    Args:
        circuits: Dictionary mapping circuit names to serialized grids.
    """
    with open(FILE_PATH, "w", encoding="utf-8") as file:
        lines = [f"{name}:{grid}" for name, grid in circuits.items()]
        file.write("\n".join(lines))