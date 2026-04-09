from __future__ import annotations

import random
from enum import Enum

from games.pixelKart.model.dto import CircuitDTO


class CellType(Enum):
    """Represent the different kinds of circuit cells."""

    ROAD = "ROAD"
    GRASS = "GRASS"
    WALL = "WALL"
    FINISH = "FINISH"

    @classmethod
    def from_letter(cls, letter: str) -> "CellType":
        """Convert a serialized letter to a CellType."""
        if letter == "R":
            return cls.ROAD
        if letter == "G":
            return cls.GRASS
        if letter == "W":
            return cls.WALL
        if letter == "F":
            return cls.FINISH
        raise ValueError(f"Unknown cell letter: {letter}")

    def to_letter(self) -> str:
        """Convert a CellType to its serialized letter."""
        if self == CellType.ROAD:
            return "R"
        if self == CellType.GRASS:
            return "G"
        if self == CellType.WALL:
            return "W"
        return "F"


class Circuit:
    """Represents a PixelKart circuit."""

    def __init__(self, name: str, grid: list[list[CellType]]) -> None:
        """
        Initialize a circuit.

        Args:
            name: Circuit name.
            grid: Two-dimensional grid of CellType values.

        Raises:
            ValueError: If the grid is empty or malformed.
        """
        if not grid or not grid[0]:
            raise ValueError("A circuit grid cannot be empty.")

        row_length = len(grid[0])
        if any(len(row) != row_length for row in grid):
            raise ValueError("All rows in the circuit grid must have the same length.")

        self.name = name
        self.grid = grid
        self.rows = len(grid)
        self.cols = row_length

    @classmethod
    def from_dto(cls, dto: CircuitDTO) -> "Circuit":
        """
        Build a Circuit instance from a CircuitDTO.

        Args:
            dto: Serialized circuit data.

        Returns:
            A Circuit instance.

        Raises:
            ValueError: If the serialized grid is invalid.
        """
        if not dto.grid:
            raise ValueError("Circuit grid cannot be empty.")

        rows_data = dto.grid.strip().split(",")
        if any(not row for row in rows_data):
            raise ValueError("Circuit rows cannot be empty.")

        grid = [
            [CellType.from_letter(letter) for letter in row_data]
            for row_data in rows_data
        ]
        return cls(dto.name, grid)

    def to_dto(self) -> CircuitDTO:
        """
        Convert the circuit to a CircuitDTO.

        Returns:
            A serialized representation of the circuit.
        """
        grid = ",".join("".join(cell.to_letter() for cell in row) for row in self.grid)
        return CircuitDTO(name=self.name, grid=grid)

    def is_inside(self, position: tuple[int, int]) -> bool:
        """Check whether a position is inside the circuit boundaries."""
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_cell_type(self, position: tuple[int, int]) -> CellType:
        """
        Return the cell type at a given position.

        Args:
            position: Grid position as (row, col).

        Returns:
            The CellType at the given position.

        Raises:
            ValueError: If the position is outside the circuit.
        """
        if not self.is_inside(position):
            raise ValueError(f"Position {position} is outside the circuit.")

        row, col = position
        return self.grid[row][col]

    def is_wall(self, position: tuple[int, int]) -> bool:
        """Return True if the given position is a wall."""
        return self.is_inside(position) and self.get_cell_type(position) == CellType.WALL

    def is_grass(self, position: tuple[int, int]) -> bool:
        """Return True if the given position is grass."""
        return self.is_inside(position) and self.get_cell_type(position) == CellType.GRASS

    def is_finish(self, position: tuple[int, int]) -> bool:
        """Return True if the given position is a finish cell."""
        return self.is_inside(position) and self.get_cell_type(position) == CellType.FINISH

    def get_start_positions(self) -> list[tuple[int, int]]:
        """
        Return all finish-line positions that can be used as starting cells.

        Returns:
            A list of (row, col) positions.

        Raises:
            ValueError: If the circuit has no finish cells.
        """
        positions = [
            (row_index, col_index)
            for row_index, row in enumerate(self.grid)
            for col_index, cell in enumerate(row)
            if cell == CellType.FINISH
        ]

        if not positions:
            raise ValueError("The circuit must contain at least one FINISH cell.")

        return positions

    def get_random_start_positions(self, number_of_karts: int) -> list[tuple[int, int]]:
        """
        Return distinct random start positions for the given number of karts.

        Args:
            number_of_karts: Number of karts to place on the finish line.

        Returns:
            A list of distinct start positions.

        Raises:
            ValueError: If there are not enough finish cells.
        """
        start_positions = self.get_start_positions()

        if number_of_karts > len(start_positions):
            raise ValueError(
                "Not enough FINISH cells to place all karts on distinct start positions."
            )

        return random.sample(start_positions, number_of_karts)