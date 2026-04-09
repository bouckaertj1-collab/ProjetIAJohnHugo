from __future__ import annotations

from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from games.pixelKart.model.dto import KartDTO, RaceDTO
from games.pixelKart.model.movement import Action
from games.pixelKart.view.circuit_frames import CircuitRaceFrame


class RaceView(ttk.Frame):
    """Display the PixelKart race screen."""

    def __init__(self, parent: tk.Misc) -> None:
        """
        Initialize the race view.

        Args:
            parent: Parent Tkinter widget.
        """
        super().__init__(parent, padding=10)
        self.pack(fill="both", expand=True)

        self.circuit_frame: CircuitRaceFrame | None = None
        self.action_callback: Callable[[Action], None] | None = None

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        left_frame = ttk.Frame(self, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)

        race_frame = ttk.LabelFrame(left_frame, text="Race", padding=10)
        race_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        race_frame.columnconfigure(0, weight=1)
        race_frame.columnconfigure(1, weight=1)

        self.time_label = ttk.Label(race_frame, text="Time: 0")
        self.time_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.turns_label = ttk.Label(race_frame, text="Turns to do: 0")
        self.turns_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.status_label = ttk.Label(race_frame, text="Race in progress")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        self.circuit_container = ttk.LabelFrame(left_frame, text="Circuit", padding=10)
        self.circuit_container.grid(row=1, column=0, sticky="nsew")
        self.circuit_container.columnconfigure(0, weight=1)
        self.circuit_container.rowconfigure(0, weight=1)

        right_frame = ttk.Frame(self, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        players_frame = ttk.LabelFrame(right_frame, text="Players", padding=10)
        players_frame.grid(row=0, column=0, sticky="nsew")
        players_frame.columnconfigure(0, weight=1)
        players_frame.rowconfigure(0, weight=1)

        self.players_canvas = tk.Canvas(players_frame, highlightthickness=0)
        self.players_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(players_frame, orient="vertical", command=self.players_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.players_canvas.configure(yscrollcommand=scrollbar.set)

        self.players_container = ttk.Frame(self.players_canvas)
        self.players_window = self.players_canvas.create_window(
            (0, 0),
            window=self.players_container,
            anchor="nw",
        )

        self.players_container.bind(
            "<Configure>",
            lambda event: self.players_canvas.configure(scrollregion=self.players_canvas.bbox("all")),
        )
        self.players_canvas.bind(
            "<Configure>",
            lambda event: self.players_canvas.itemconfigure(self.players_window, width=event.width),
        )

    def bind_action(self, callback: Callable[[Action], None]) -> None:
        """
        Bind all action buttons to one callback.

        Args:
            callback: Function receiving the selected action.
        """
        self.action_callback = callback

    def set_circuit(self, serialized_grid: str) -> None:
        """
        Create or refresh the circuit widget.

        Args:
            serialized_grid: Serialized circuit grid.
        """
        if self.circuit_frame is not None:
            self.circuit_frame.destroy()

        self.circuit_frame = CircuitRaceFrame(self.circuit_container, circuit=serialized_grid)
        self.circuit_frame.grid(row=0, column=0, sticky="nsew")

    def update_view(self, race_dto: RaceDTO, kart_dtos: list[KartDTO], current_kart_name: str) -> None:
        """
        Update the view of the full race screen.

        Args:
            race_dto: Global race state.
            kart_dtos: State of all karts.
            current_kart_name: Name of the current kart.
        """
        self.time_label.config(text=f"Time: {race_dto.time}")
        self.turns_label.config(text=f"Turns to do: {race_dto.total_laps}")

        if not race_dto.finished:
            self.status_label.config(text=f"Current player: {current_kart_name}")
        elif race_dto.winner_name is None:
            self.status_label.config(text="Race finished: no winner")
        else:
            self.status_label.config(text=f"Race finished: winner is {race_dto.winner_name}")

        for child in self.players_container.winfo_children():
            child.destroy()

        self.players_container.columnconfigure(0, weight=1)
        self.players_container.columnconfigure(1, weight=1)

        circuit_karts: dict[tuple[int, int], tuple[str, str]] = {}

        for index, kart_dto in enumerate(kart_dtos):
            row = index // 2
            column = index % 2

            panel = ttk.LabelFrame(
                self.players_container,
                text=f"Kart {kart_dto.name}",
                padding=10,
            )
            panel.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
            panel.columnconfigure(0, weight=1)
            panel.columnconfigure(1, weight=1)

            ttk.Label(panel, text=f"Position : {kart_dto.position}").grid(
                row=0, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )
            ttk.Label(panel, text=f"Direction : {kart_dto.direction}").grid(
                row=1, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )
            ttk.Label(panel, text=f"Speed : {kart_dto.speed}").grid(
                row=2, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )
            ttk.Label(panel, text=f"Turns done : {kart_dto.laps_done}").grid(
                row=3, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )

            next_row = 4
            if not kart_dto.is_alive:
                ttk.Label(panel, text="Status : eliminated").grid(
                    row=next_row, column=0, columnspan=2, sticky="w", padx=5, pady=4
                )
                next_row += 1

            play_frame = ttk.LabelFrame(panel, text="Play", padding=8)
            play_frame.grid(
                row=next_row,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=5,
                pady=(8, 0),
            )
            play_frame.columnconfigure(0, weight=1)
            play_frame.columnconfigure(1, weight=1)

            enabled = (
                not race_dto.finished
                and kart_dto.is_alive
                and not kart_dto.is_ai
                and kart_dto.name == current_kart_name
            )
            state = "normal" if enabled else "disabled"

            ttk.Button(
                play_frame,
                text="Accelerate",
                width=12,
                state=state,
                command=lambda: self._on_action(Action.ACCELERATE),
            ).grid(row=0, column=0, columnspan=2, pady=4)

            ttk.Button(
                play_frame,
                text="Turn Left",
                width=10,
                state=state,
                command=lambda: self._on_action(Action.TURN_LEFT),
            ).grid(row=1, column=0, padx=4, pady=4)

            ttk.Button(
                play_frame,
                text="Turn Right",
                width=10,
                state=state,
                command=lambda: self._on_action(Action.TURN_RIGHT),
            ).grid(row=1, column=1, padx=4, pady=4)

            ttk.Button(
                play_frame,
                text="Brake",
                width=12,
                state=state,
                command=lambda: self._on_action(Action.BRAKE),
            ).grid(row=2, column=0, columnspan=2, pady=4)

            ttk.Button(
                play_frame,
                text="Pass",
                width=12,
                state=state,
                command=lambda: self._on_action(Action.PASS),
            ).grid(row=3, column=0, columnspan=2, pady=4)

            if kart_dto.is_alive:
                circuit_karts[kart_dto.position] = (kart_dto.color, kart_dto.direction)

        if self.circuit_frame is not None:
            self.circuit_frame.update_view(circuit_karts)

    def _on_action(self, action: Action) -> None:
        """
        Call the bound action callback.

        Args:
            action: Selected action.
        """
        if self.action_callback is not None:
            self.action_callback(action)