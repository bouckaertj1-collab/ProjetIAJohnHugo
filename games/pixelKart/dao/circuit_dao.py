from __future__ import annotations

from pathlib import Path

from games.PixelKart.model.dto import CircuitDTO


FILE_PATH = Path(__file__).resolve().parent.parent / "circuits.txt"


def get_all() -> dict[str, CircuitDTO]:
    """
    Retrieve all circuits from the file.

    Returns:
        A dictionary mapping circuit names to CircuitDTO objects.
    """
    circuits: dict[str, CircuitDTO] = {}

    if not FILE_PATH.exists():
        return circuits

    with FILE_PATH.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line or ":" not in line:
                continue

            name, grid = line.split(":", maxsplit=1)
            name = name.strip()
            grid = grid.strip()

            if name and grid:
                circuits[name] = CircuitDTO(name=name, grid=grid)

    return circuits


def get_by_name(name: str) -> CircuitDTO | None:
    """
    Retrieve a circuit by its name.

    Args:
        name: Circuit name.

    Returns:
        The matching CircuitDTO, or None if not found.
    """
    return get_all().get(name)


def save_circuit(name: str, grid: str) -> None:
    """
    Save a new circuit.

    Args:
        name: Circuit name.
        grid: Serialized circuit.

    Raises:
        ValueError: If the name or grid is empty, or if the circuit already exists.
    """
    if not name.strip():
        raise ValueError("Circuit name cannot be empty.")

    if not grid.strip():
        raise ValueError("Circuit grid cannot be empty.")

    circuits = get_all()

    if name in circuits:
        raise ValueError(f"The circuit '{name}' already exists.")

    circuits[name] = CircuitDTO(name=name, grid=grid)
    _write_all(circuits)


def update_circuit(name: str, grid: str) -> None:
    """
    Update an existing circuit.

    Args:
        name: Circuit name.
        grid: New serialized circuit.

    Raises:
        ValueError: If the circuit does not exist.
    """
    circuits = get_all()

    if name not in circuits:
        raise ValueError(f"The circuit '{name}' does not exist.")

    circuits[name] = CircuitDTO(name=name, grid=grid)
    _write_all(circuits)


def delete_circuit(name: str) -> None:
    """
    Delete a circuit.

    Args:
        name: Circuit name.

    Raises:
        ValueError: If the circuit does not exist.
    """
    circuits = get_all()

    if name not in circuits:
        raise ValueError(f"The circuit '{name}' does not exist.")

    del circuits[name]
    _write_all(circuits)


def _write_all(circuits: dict[str, CircuitDTO]) -> None:
    """
    Rewrite the full circuits file.

    Args:
        circuits: Circuits to persist.
    """
    with FILE_PATH.open("w", encoding="utf-8") as file:
        lines = [f"{dto.name}:{dto.grid}" for dto in circuits.values()]
        file.write("\n".join(lines))