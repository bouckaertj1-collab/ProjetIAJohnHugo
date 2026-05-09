from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class MenuView(ttk.Frame):
    """Display the PixelKart configuration menu."""

    def __init__(self, parent: tk.Misc) -> None:
        """
        Initialize the menu view.

        Args:
            parent: Parent Tkinter widget.
        """
        super().__init__(parent, padding=15)
        self.pack(fill="both", expand=True)

        self.human_players_var = tk.IntVar(value=1)
        self.random_ais_var = tk.IntVar(value=0)
        self.ql_ais_var = tk.IntVar(value=1)
        self.laps_var = tk.IntVar(value=2)
        self.selected_circuit_var = tk.StringVar(value="")

        title_label = ttk.Label(self, text="PixelKart", font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 15))

        config_frame = ttk.LabelFrame(self, text="Game configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(config_frame, text="Human players:").grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Spinbox(
            config_frame,
            from_=0,
            to=4,
            textvariable=self.human_players_var,
            width=10,
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(config_frame, text="Random AIs:").grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Spinbox(
            config_frame,
            from_=0,
            to=4,
            textvariable=self.random_ais_var,
            width=10,
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(config_frame, text="QLearning AIs:").grid(
            row=2,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Spinbox(
            config_frame,
            from_=0,
            to=4,
            textvariable=self.ql_ais_var,
            width=10,
        ).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(config_frame, text="Laps:").grid(
            row=3,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        ttk.Spinbox(
            config_frame,
            from_=1,
            to=20,
            textvariable=self.laps_var,
            width=10,
        ).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(config_frame, text="Circuit:").grid(
            row=4,
            column=0,
            sticky="w",
            padx=5,
            pady=5,
        )
        self.circuit_combobox = ttk.Combobox(
            config_frame,
            textvariable=self.selected_circuit_var,
            state="readonly",
            width=20,
        )
        self.circuit_combobox.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        self.open_editor_button = ttk.Button(button_frame, text="Open circuit editor")
        self.open_editor_button.pack(side="left", padx=5)

        self.refresh_button = ttk.Button(button_frame, text="Refresh circuits")
        self.refresh_button.pack(side="left", padx=5)

        self.play_button = ttk.Button(button_frame, text="Play")
        self.play_button.pack(side="left", padx=5)

        self.message_label = ttk.Label(self, text="", foreground="red")
        self.message_label.pack(pady=(5, 0))

    def bind_actions(self, play_callback, editor_callback, refresh_callback) -> None:
        """
        Bind all menu buttons.

        Args:
            play_callback: Callback for the Play button.
            editor_callback: Callback for the circuit editor button.
            refresh_callback: Callback for the refresh button.
        """
        self.play_button.config(command=play_callback)
        self.open_editor_button.config(command=editor_callback)
        self.refresh_button.config(command=refresh_callback)

    def get_config(self) -> tuple[int, int, int, int, str]:
        """
        Return the current menu configuration.

        Returns:
            A tuple containing human players, random AI players,
            QLearning AI players, laps and circuit name.
        """
        return (
            self.human_players_var.get(),
            self.random_ais_var.get(),
            self.ql_ais_var.get(),
            self.laps_var.get(),
            self.selected_circuit_var.get().strip(),
        )

    def set_circuits(self, circuit_names: list[str]) -> None:
        """
        Update the list of available circuits.

        Args:
            circuit_names: Names of the available circuits.
        """
        self.circuit_combobox["values"] = circuit_names

        if not circuit_names:
            self.selected_circuit_var.set("")
        elif self.selected_circuit_var.get() not in circuit_names:
            self.selected_circuit_var.set(circuit_names[0])

    def set_selected_circuit(self, circuit_name: str) -> None:
        """
        Set the selected circuit.

        Args:
            circuit_name: Circuit name to select.
        """
        self.selected_circuit_var.set(circuit_name)

    def set_message(self, message: str) -> None:
        """
        Display a message to the user.

        Args:
            message: Message to display.
        """
        self.message_label.config(text=message)