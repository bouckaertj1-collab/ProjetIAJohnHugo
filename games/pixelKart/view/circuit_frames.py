from __future__ import annotations

import tkinter as tk
from tkinter import ttk


PIXEL_TYPES = {
    "ROAD": {"color": "grey", "letter": "R"},
    "GRASS": {"color": "green", "letter": "G"},
    "WALL": {"color": "black", "letter": "W"},
    "FINISH": {"color": "yellow", "letter": "F"},
}


class CircuitFrame(ttk.Frame):
    """Base widget displaying a circuit grid."""

    def __init__(
        self,
        container: tk.Misc,
        circuit: str | None = None,
        rows: int = 12,
        cols: int = 20,
    ) -> None:
        """
        Initialize a circuit grid frame.

        Args:
            container: Parent Tkinter widget.
            circuit: Serialized circuit to load, if provided.
            rows: Number of grid rows.
            cols: Number of grid columns.
        """
        super().__init__(container)
        self.rows = rows
        self.cols = cols
        self.cells: list[list[tk.Label]] = []

        self.init_cells()

        if circuit:
            self.dto_to_grid(circuit)

    def init_cells(self) -> None:
        """Create the grid cells with grass borders and road inside."""
        for line in range(self.rows):
            row: list[tk.Label] = []

            for col in range(self.cols):
                initial_type = (
                    "GRASS"
                    if 0 in (line, col) or line == self.rows - 1 or col == self.cols - 1
                    else "ROAD"
                )
                initial_color = PIXEL_TYPES[initial_type]["color"]

                cell = tk.Label(
                    self,
                    bg=initial_color,
                    width=2,
                    height=1,
                    borderwidth=1,
                    relief="solid",
                )
                cell.grid(row=line, column=col, sticky="nsew")
                row.append(cell)

            self.cells.append(row)

        for i in range(self.rows):
            self.grid_rowconfigure(i, weight=1, minsize=20)

        for j in range(self.cols):
            self.grid_columnconfigure(j, weight=1, minsize=20)

    def clear(self) -> None:
        """Remove all grid cells."""
        for widget in self.winfo_children():
            widget.destroy()

        self.cells.clear()

    def grid_to_dto(self) -> str:
        """
        Serialize the grid.

        Returns:
            Circuit string using R, G, W and F letters.
        """
        export_result = []
        color_map = {value["color"]: value["letter"] for value in PIXEL_TYPES.values()}

        for row in self.cells:
            export_result.append("".join(color_map[cell.cget("bg")] for cell in row))

        return ",".join(export_result)

    def dto_to_grid(self, dto: str) -> None:
        """
        Load a serialized circuit into the grid.

        Args:
            dto: Circuit string using R, G, W and F letters.
        """
        import_data = dto.split(",")
        if not import_data:
            return

        self.rows = len(import_data)
        self.cols = len(import_data[0])

        self.clear()
        self.init_cells()

        color_map = {value["letter"]: value["color"] for value in PIXEL_TYPES.values()}

        for i, row in enumerate(import_data):
            for j, char in enumerate(row):
                if i < len(self.cells) and j < len(self.cells[i]):
                    self.cells[i][j].config(bg=color_map.get(char, "grey"))


class CircuitEditorFrame(CircuitFrame):
    """Editable circuit grid used by the circuit editor."""

    def init_cells(self) -> None:
        """Create the grid cells and bind clicks to color changes."""
        super().init_cells()

        for line in range(self.rows):
            for col in range(self.cols):
                cell = self.cells[line][col]
                cell.bind("<Button-1>", lambda event, x=line, y=col: self.change_color(x, y))

    def change_color(self, x: int, y: int) -> None:
        """
        Change a cell to the next terrain color.

        Args:
            x: Cell row.
            y: Cell column.
        """
        current_color = self.cells[x][y].cget("bg")
        colors = [pixel["color"] for pixel in PIXEL_TYPES.values()]
        new_color = colors[(colors.index(current_color) + 1) % len(colors)]
        self.cells[x][y].config(bg=new_color)


class CircuitRaceFrame(CircuitFrame):
    """Circuit grid used to display a race and its karts."""

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
            circuit: Serialized circuit to load, if provided.
            rows: Number of grid rows.
            cols: Number of grid columns.
        """
        super().__init__(container, circuit, rows, cols)
        self.karts_cells: list[tk.Label] = []

    def update_view(self, karts: dict) -> None:
        """
        Display the karts on the circuit.

        Args:
            karts: Mapping from positions to kart display data.
        """
        for cell in self.karts_cells:
            cell.destroy()
        self.karts_cells.clear()

        arrows = {
            "NORTH": "↑",
            "EAST": "→",
            "SOUTH": "↓",
            "WEST": "←",
        }

        for position, value in karts.items():
            line, col = position

            if isinstance(value, tuple):
                color, direction = value
                text = arrows.get(direction, "")
            else:
                color = value
                text = ""

            if 0 <= line < self.rows and 0 <= col < self.cols:
                cell = tk.Label(
                    self,
                    bg=color,
                    fg="white",
                    text=text,
                    width=2,
                    height=1,
                    borderwidth=1,
                    relief="solid",
                    font=("Arial", 10, "bold"),
                )
                cell.grid(row=line, column=col, sticky="nsew")
                self.karts_cells.append(cell)