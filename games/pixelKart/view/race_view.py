from collections.abc import Callable
import tkinter as tk
from tkinter import ttk

from games.pixelKart.model.dto import KartDTO, RaceDTO
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
        self.action_callback: Callable[[str], None] | None = None

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

        scrollbar = ttk.Scrollbar(
            players_frame,
            orient="vertical",
            command=self.players_canvas.yview,
        )
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
            lambda event: self.players_canvas.configure(
                scrollregion=self.players_canvas.bbox("all")
            ),
        )
        self.players_canvas.bind(
            "<Configure>",
            lambda event: self.players_canvas.itemconfigure(
                self.players_window,
                width=event.width,
            ),
        )

        game_frame = ttk.LabelFrame(right_frame, text="Game", padding=10)
        game_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        game_frame.columnconfigure(0, weight=1)

        self.back_to_menu_button = ttk.Button(game_frame, text="Back to menu", width=18)
        self.back_to_menu_button.grid(row=0, column=0, pady=5)

    def bind_back_to_menu(self, callback) -> None:
        """
        Bind the back-to-menu button.

        Args:
            callback: Function called when the button is clicked.
        """
        self.back_to_menu_button.config(command=callback)

    def set_circuit(self, serialized_grid: str) -> None:
        """
        Display a circuit grid.

        Args:
            serialized_grid: Serialized circuit layout.
        """
        if self.circuit_frame is not None:
            self.circuit_frame.destroy()

        self.circuit_frame = CircuitRaceFrame(
            self.circuit_container,
            circuit=serialized_grid,
        )
        self.circuit_frame.grid(row=0, column=0, sticky="nsew")

    def update_view(
        self,
        race_dto: RaceDTO,
        kart_dtos: list[KartDTO],
        current_kart_name: str,
    ) -> None:
        """
        Refresh the race screen from DTO data.

        Args:
            race_dto: Current race state.
            kart_dtos: Current state of all karts.
            current_kart_name: Name of the kart whose turn is active.
        """
        self.time_label.config(text=f'Time: {race_dto["time"]}')

        current_kart_dto = next(k for k in kart_dtos if k["name"] == current_kart_name)
        turns_left = max(0, race_dto["total_laps"] - current_kart_dto["laps_done"])

        if race_dto["finished"] and race_dto["winner_name"] is not None:
            winner_dto = next(
                k for k in kart_dtos
                if k["name"] == race_dto["winner_name"]
            )
            self.turns_label.config(
                text=f'Winner turns: {winner_dto["laps_done"]}/{race_dto["total_laps"]}'
            )
        else:
            self.turns_label.config(text=f"Turns to do: {turns_left}")

        if not race_dto["finished"]:
            self.status_label.config(text=f"Current player: {current_kart_name}")
        elif race_dto["winner_name"] is None:
            self.status_label.config(text="Race finished: no winner")
        else:
            self.status_label.config(text=f'Race finished: winner is {race_dto["winner_name"]}')

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
                text=f'Kart {kart_dto["name"]}',
                padding=10,
            )
            panel.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
            panel.columnconfigure(0, weight=1)
            panel.columnconfigure(1, weight=1)

            ttk.Label(panel, text=f'Position : {kart_dto["position"]}').grid(
                row=0, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )
            ttk.Label(panel, text=f'Direction : {kart_dto["direction"]}').grid(
                row=1, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )
            ttk.Label(panel, text=f'Speed : {kart_dto["speed"]}').grid(
                row=2, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )
            ttk.Label(panel, text=f'Turns done : {kart_dto["laps_done"]}').grid(
                row=3, column=0, columnspan=2, sticky="w", padx=5, pady=4
            )

            next_row = 4

            if race_dto["winner_name"] == kart_dto["name"]:
                ttk.Label(panel, text="Winner : yes").grid(
                    row=next_row,
                    column=0,
                    columnspan=2,
                    sticky="w",
                    padx=5,
                    pady=4,
                )
                next_row += 1

            if kart_dto["has_finished"]:
                ttk.Label(panel, text="Status : finished").grid(
                    row=next_row,
                    column=0,
                    columnspan=2,
                    sticky="w",
                    padx=5,
                    pady=4,
                )
                next_row += 1
            elif not kart_dto["is_alive"]:
                ttk.Label(panel, text="Status : eliminated").grid(
                    row=next_row,
                    column=0,
                    columnspan=2,
                    sticky="w",
                    padx=5,
                    pady=4,
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
                not race_dto["finished"]
                and kart_dto["is_alive"]
                and not kart_dto["has_finished"]
                and not kart_dto["is_ai"]
                and kart_dto["name"] == current_kart_name
            )
            state = "normal" if enabled else "disabled"

            ttk.Button(
                play_frame,
                text="Accelerate",
                width=12,
                state=state,
                command=lambda: self._on_action("accelerate"),
            ).grid(row=0, column=0, columnspan=2, pady=4)

            ttk.Button(
                play_frame,
                text="Turn Left",
                width=10,
                state=state,
                command=lambda: self._on_action("turn_left"),
            ).grid(row=1, column=0, padx=4, pady=4)

            ttk.Button(
                play_frame,
                text="Turn Right",
                width=10,
                state=state,
                command=lambda: self._on_action("turn_right"),
            ).grid(row=1, column=1, padx=4, pady=4)

            ttk.Button(
                play_frame,
                text="Brake",
                width=12,
                state=state,
                command=lambda: self._on_action("brake"),
            ).grid(row=2, column=0, columnspan=2, pady=4)

            ttk.Button(
                play_frame,
                text="Pass",
                width=12,
                state=state,
                command=lambda: self._on_action("pass"),
            ).grid(row=3, column=0, columnspan=2, pady=4)

            if kart_dto["is_alive"] and not kart_dto["has_finished"]:
                display_direction = kart_dto["direction"]

                if kart_dto["speed"] < 0:
                    opposite = {
                        "NORTH": "SOUTH",
                        "SOUTH": "NORTH",
                        "EAST": "WEST",
                        "WEST": "EAST",
                    }
                    display_direction = opposite[display_direction]

                circuit_karts[kart_dto["position"]] = (
                    kart_dto["color"],
                    display_direction,
                )

        if self.circuit_frame is not None:
            self.circuit_frame.update_view(circuit_karts)

    def _on_action(self, action: str) -> None:
        """
        Send a selected action to the bound callback.

        Args:
            action: Selected action.
        """
        if self.action_callback is not None:
            self.action_callback(action)
            
    def bind_action(self, callback: Callable[[str], None]) -> None:
        """
        Store the callback used when an action button is clicked.

        Args:
            callback: Function receiving the selected action.
        """
        self.action_callback = callback