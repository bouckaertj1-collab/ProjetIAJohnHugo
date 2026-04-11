from __future__ import annotations

import tkinter as tk
from tkinter import Tk, ttk

from games.PixelKart.dao import circuit_dao as dao
from games.PixelKart.view.circuit_frames import CircuitEditorFrame


class CircuitEditor(tk.Toplevel):
    """
    Display a secondary window used to create, import and save circuits.
    """

    def __init__(self, parent: tk.Misc, callback) -> None:
        """
        Initialize the circuit editor window.

        Args:
            parent: Parent Tkinter window.
            callback: Function called with the selected circuit name.
        """
        super().__init__(parent)
        self.title("Circuit Editor")

        self.callback = callback
        self.length_var = tk.StringVar(value="20")
        self.width_var = tk.StringVar(value="12")
        self.circuit_var = tk.StringVar()

        input_frame = ttk.Frame(self)
        input_frame.pack(pady=5, fill="x")

        ttk.Label(input_frame, text="Length:").pack(side="left", padx=5)
        ttk.Entry(input_frame, textvariable=self.length_var, width=5).pack(side="left")

        ttk.Label(input_frame, text="Width:").pack(side="left", padx=5)
        ttk.Entry(input_frame, textvariable=self.width_var, width=5).pack(side="left")

        ttk.Button(input_frame, text="Change size", command=self.change_size).pack(
            side="left",
            padx=5,
        )

        self.grid_frame = CircuitEditorFrame(self)
        self.grid_frame.pack(pady=10, fill="both", expand=True)

        import_frame = ttk.Frame(self)
        import_frame.pack(pady=5, fill="x")

        ttk.Label(import_frame, text="Import circuit:").pack(side="left", padx=5)
        self.circuit_dropdown = tk.OptionMenu(import_frame, self.circuit_var, "")
        self.circuit_dropdown.pack(side="left", padx=5)

        ttk.Button(import_frame, text="Import", command=self.import_circuit).pack(
            side="left",
            padx=5,
        )

        save_frame = ttk.Frame(self)
        save_frame.pack(pady=5, fill="x")

        ttk.Button(save_frame, text="Save", command=self.save_circuit).pack(
            side="left",
            padx=5,
        )
        ttk.Button(save_frame, text="Choose", command=self.choose).pack(
            side="left",
            padx=5,
        )

        self.refresh_circuits()

    def refresh_circuits(self) -> None:
        """Reload available circuits from the DAO and refresh the dropdown."""
        self.all_circuits = dao.get_all()
        circuit_names = list(self.all_circuits.keys())

        menu = self.circuit_dropdown["menu"]
        menu.delete(0, "end")

        for name in circuit_names:
            menu.add_command(label=name, command=tk._setit(self.circuit_var, name))

        self.circuit_var.set(circuit_names[0] if circuit_names else "")

    def choose(self) -> None:
        """Call the callback with the selected circuit name."""
        self.callback(self.circuit_var.get())

    def import_circuit(self) -> None:
        """Import the selected circuit into the grid."""
        circuit_name = self.circuit_var.get()
        dto = self.all_circuits.get(circuit_name)

        if dto is None:
            return

        self.grid_frame.dto_to_grid(dto.grid)
        self.length_var.set(str(self.grid_frame.cols))
        self.width_var.set(str(self.grid_frame.rows))

    def save_circuit(self) -> None:
        """Open a popup asking for a circuit name and save it."""
        popup = tk.Toplevel(self)
        popup.title("Save Circuit")

        ttk.Label(popup, text="Circuit Name:").pack(pady=5)

        name_var = tk.StringVar()
        ttk.Entry(popup, textvariable=name_var).pack(pady=5)

        def save_action() -> None:
            try:
                dao.save_circuit(name_var.get().strip(), self.grid_frame.grid_to_dto())
                self.refresh_circuits()
                self.circuit_var.set(name_var.get().strip())
                popup.destroy()
            except Exception as error:
                error_popup = tk.Toplevel(self)
                error_popup.title("Error")
                ttk.Label(error_popup, text=f"An error occurred: {error}").pack(pady=10)
                ttk.Button(error_popup, text="OK", command=error_popup.destroy).pack(pady=5)

        ttk.Button(popup, text="Save", command=save_action).pack(pady=5)

    def change_size(self) -> None:
        """Change the grid size according to the entry values."""
        try:
            rows = int(self.width_var.get())
        except ValueError:
            rows = 12
            self.width_var.set("12")

        try:
            cols = int(self.length_var.get())
        except ValueError:
            cols = 20
            self.length_var.set("20")

        self.grid_frame.rows = rows
        self.grid_frame.cols = cols
        self.grid_frame.clear()
        self.grid_frame.init_cells()


if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    editor = CircuitEditor(root, callback=lambda name: print(f"Callback with {name}"))
    editor.mainloop()