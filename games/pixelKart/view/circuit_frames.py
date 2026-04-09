from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from games.pixelKart.model.circuit import CellType


CELL_COLORS = {
    CellType.ROAD: "grey",
    CellType.GRASS: "green",
    CellType.WALL: "black",
    CellType.FINISH: "yellow",
}

LETTER_TO_COLOR = {
    "R": "grey",
    "G": "green",
    "W": "black",
    "F": "yellow",
}

COLOR_TO_LETTER = {
    "grey": "R",
    "green": "G",
    "black": "W",
    "yellow": "F",
}

ARROWS = {
    "NORTH": "↑",
    "EAST": "→",
    "SOUTH": "↓",
    "WEST": "←",
}


class CircuitFrame(ttk.Frame):
    """
    CircuitFrame is a custom ttk.Frame widget that represents a grid-based circuit.
    The class provides functionality to initialize the grid, clear it,
    and serialize/deserialize the grid state for saving and loading purposes.

    Attributes:
        rows (int): Number of rows in the grid.
        cols (int): Number of columns in the grid.
        cells (list[list[tk.Label]]): A 2D list of Tkinter Label widgets representing the grid cells.
    """

    def __init__(
        self,
        container: tk.Misc,
        circuit: str | None = None,
        rows: int = 12,
        cols: int = 20,
    ) -> None:
        """
        Initialize the circuit frame.

        Args:
            container: Parent Tkinter widget.
            circuit: Optional serialized circuit string.
            rows: Number of rows.
            cols: Number of columns.
        """
        super().__init__(container)
        self.rows = rows
        self.cols = cols
        self.cells: list[list[tk.Label]] = []

        self.init_cells()

        if circuit:
            self.dto_to_grid(circuit)

    def init_cells(self) -> None:
        """Initialize the grid with default colors."""
        for row in range(self.rows):
            current_row: list[tk.Label] = []

            for col in range(self.cols):
                if 0 in (row, col) or row == self.rows - 1 or col == self.cols - 1:
                    color = CELL_COLORS[CellType.GRASS]
                else:
                    color = CELL_COLORS[CellType.ROAD]

                cell = tk.Label(
                    self,
                    bg=color,
                    width=2,
                    height=1,
                    borderwidth=1,
                    relief="solid",
                )
                cell.grid(row=row, column=col, sticky="nsew")
                current_row.append(cell)

            self.cells.append(current_row)

        for row in range(self.rows):
            self.grid_rowconfigure(row, weight=1, minsize=20)

        for col in range(self.cols):
            self.grid_columnconfigure(col, weight=1, minsize=20)

    def clear(self) -> None:
        """Clear the grid widgets."""
        for widget in self.winfo_children():
            widget.destroy()
        self.cells.clear()

    def grid_to_dto(self) -> str:
        """
        Serialize the displayed grid to a DTO string.

        Returns:
            A serialized grid string like 'RGF,GGW,RRR'.
        """
        rows = []
        for row in self.cells:
            rows.append("".join(COLOR_TO_LETTER[cell.cget("bg")] for cell in row))
        return ",".join(rows)

    def dto_to_grid(self, dto: str) -> None:
        """
        Load a serialized grid into the frame.

        Args:
            dto: Serialized grid string like 'RGF,GGW,RRR'.
        """
        grid_data = dto.split(",")
        if not grid_data:
            return

        self.rows = len(grid_data)
        self.cols = len(grid_data[0])

        self.clear()
        self.init_cells()

        for row_index, row in enumerate(grid_data):
            for col_index, letter in enumerate(row):
                self.cells[row_index][col_index].config(
                    bg=LETTER_TO_COLOR.get(letter, CELL_COLORS[CellType.ROAD])
                )


class CircuitEditorFrame(CircuitFrame):
    """Display an editable circuit grid."""

    def init_cells(self) -> None:
        """Initialize cells and bind click events for editing."""
        super().init_cells()

        for row in range(self.rows):
            for col in range(self.cols):
                self.cells[row][col].bind(
                    "<Button-1>",
                    lambda event, x=row, y=col: self.change_color(x, y),
                )

    def change_color(self, row: int, col: int) -> None:
        """
        Cycle the cell color at the given coordinates.

        Args:
            row: Row index.
            col: Column index.
        """
        current_color = self.cells[row][col].cget("bg")

        if current_color == "grey":
            new_color = "green"
        elif current_color == "green":
            new_color = "black"
        elif current_color == "black":
            new_color = "yellow"
        else:
            new_color = "grey"

        self.cells[row][col].config(bg=new_color)


class CircuitRaceFrame(CircuitFrame):
    """Display a race circuit and overlay karts on it."""

    def __init__(
        self,
        container: tk.Misc,
        circuit: str | None = None,
        rows: int = 12,
        cols: int = 20,
    ) -> None:
        """
        Initialize the race circuit frame.

        Args:
            container: Parent Tkinter widget.
            circuit: Optional serialized circuit string.
            rows: Number of rows.
            cols: Number of columns.
        """
        super().__init__(container, circuit, rows, cols)
        self.karts_cells: list[tk.Label] = []

    def update_view(self, karts: dict[tuple[int, int], tuple[str, str]]) -> None:
        """
        Update the circuit overlay with kart positions.

        Args:
            karts: Dictionary mapping position to (color, direction_name).
        """
        for cell in self.karts_cells:
            cell.destroy()
        self.karts_cells.clear()

        for (row, col), (color, direction_name) in karts.items():
            if 0 <= row < self.rows and 0 <= col < self.cols:
                cell = tk.Label(
                    self,
                    bg=color,
                    fg="white",
                    text=ARROWS.get(direction_name, "?"),
                    width=2,
                    height=1,
                    borderwidth=1,
                    relief="solid",
                    font=("Arial", 10, "bold"),
                )
                cell.grid(row=row, column=col, sticky="nsew")
                self.karts_cells.append(cell)