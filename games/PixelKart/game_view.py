"""Tkinter view for PixelKart."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_controller import GameController


class GameView(tk.Toplevel):
    """Dark themed view for the PixelKart race."""

    BG = "#050609"
    PANEL = "#10141f"
    PANEL_ALT = "#151b27"
    TEXT = "#e5edf5"
    MUTED = "#91a0b6"
    ACCENT = "#22c55e"
    WARNING = "#facc15"

    PIXEL_COLORS: dict[str, str] = {
        "road": "#222833",
        "grass": "#0f6b1f",
        "wall": "#020204",
        "start": "#facc15",
    }

    ACTIONS: tuple[tuple[str, str], ...] = (
        ("Accelerer", "accelerate"),
        ("Freiner", "brake"),
        ("Gauche", "turn_left"),
        ("Droite", "turn_right"),
        ("Attendre", "wait"),
    )

    def __init__(self, parent: tk.Tk, controller: "GameController", cell_size: int = 26) -> None:
        """
        Initialize the PixelKart game window.

        Args:
            parent: Parent Tk window.
            controller: Game controller.
            cell_size: Size of one circuit pixel in the canvas.
        """
        super().__init__(parent)

        self.controller = controller
        self.controller.view = self
        self.cell_size = cell_size
        self.player_count_var = tk.IntVar(value=self.controller.get_player_count())
        self.laps_choice_var = tk.IntVar(value=self.controller.get_laps_count())

        self.title("PixelKart")
        self.configure(bg=self.BG)
        self.resizable(False, False)

        self._build_ui()

    def _build_ui(self) -> None:
        """Create all widgets."""
        shell = tk.Frame(self, bg=self.BG, padx=18, pady=18)
        shell.pack(fill="both", expand=True)

        header = tk.Frame(shell, bg=self.BG)
        header.pack(fill="x", pady=(0, 14))

        tk.Label(
            header,
            text="PIXELKART",
            bg=self.BG,
            fg=self.TEXT,
            font=("Consolas", 24, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Course tour par tour: joue une action, puis le kart avance.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Consolas", 10),
        ).pack(anchor="w")

        setup = tk.Frame(shell, bg=self.PANEL, padx=12, pady=10)
        setup.pack(fill="x", pady=(0, 14))

        tk.Label(setup, text="Joueurs", bg=self.PANEL, fg=self.TEXT, font=("Consolas", 10, "bold")).pack(
            side="left"
        )

        self.player_spinbox = tk.Spinbox(
            setup,
            from_=1,
            to=3,
            width=4,
            textvariable=self.player_count_var,
            bg="#e5e7eb",
            relief="flat",
        )
        self.player_spinbox.pack(side="left", padx=(8, 14))

        tk.Label(setup, text="Nombre de tours", bg=self.PANEL, fg=self.TEXT, font=("Consolas", 10, "bold")).pack(
            side="left"
        )

        self.laps_choice_spinbox = tk.Spinbox(
            setup,
            from_=1,
            to=20,
            width=4,
            textvariable=self.laps_choice_var,
            bg="#e5e7eb",
            relief="flat"
        )
        self.laps_choice_spinbox.pack(side="left", padx=(8, 14))

        tk.Button(
            setup,
            text="Nouvelle course",
            command=self._on_new_game,
            bg=self.ACCENT,
            fg="#06120a",
            activebackground="#16a34a",
            relief="flat",
            padx=12,
        ).pack(side="left")

        tk.Button(
            setup,
            text="Reset",
            command=self.controller.reset,
            bg="#293244",
            fg=self.TEXT,
            activebackground="#374151",
            activeforeground=self.TEXT,
            relief="flat",
            padx=12,
        ).pack(side="left", padx=8)

        content = tk.Frame(shell, bg=self.BG)
        content.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(content, bg=self.BG, highlightthickness=0)
        self.canvas.pack(side="left", padx=(0, 16))

        side = tk.Frame(content, bg=self.BG)
        side.pack(side="left", fill="y")

        self.status_label = tk.Label(
            side,
            text="",
            bg=self.PANEL,
            fg=self.TEXT,
            justify="left",
            anchor="w",
            width=34,
            padx=12,
            pady=10,
            font=("Consolas", 10, "bold"),
        )
        self.status_label.pack(fill="x", pady=(0, 12))

        self.scoreboard_frame = tk.Frame(side, bg=self.BG)
        self.scoreboard_frame.pack(fill="x", pady=(0, 12))

        controls = tk.Frame(side, bg=self.PANEL, padx=10, pady=10)
        controls.pack(fill="x")

        self.action_buttons: list[tk.Button] = []
        for index, (label, action) in enumerate(self.ACTIONS):
            button = tk.Button(
                controls,
                text=label,
                command=lambda selected=action: self.controller.handle_action(selected),
                bg="#1f2937",
                fg=self.TEXT,
                activebackground=self.ACCENT,
                activeforeground="#06120a",
                relief="flat",
                width=13,
                pady=6,
            )
            button.grid(row=index // 2, column=index % 2, padx=4, pady=4, sticky="ew")
            self.action_buttons.append(button)

    def update_view(self, state: dict) -> None:
        """Refresh the full interface from a model state."""
        self.status_label.config(text=self.controller.get_status_message())
        self._draw_track(state)
        self._draw_scoreboard(state)
        self._set_action_buttons_state("disabled" if state["is_game_over"] else "normal")

    def end_game(self, message: str, state: dict) -> None:
        """Show the final race result."""
        self.update_view(state)
        messagebox.showinfo("PixelKart", message)

    def _draw_track(self, state: dict) -> None:
        """Draw the circuit and every kart."""
        height, width = state["size"]
        canvas_width = width * self.cell_size
        canvas_height = height * self.cell_size
        self.canvas.config(width=canvas_width, height=canvas_height)
        self.canvas.delete("all")

        for row_index, row in enumerate(state["track"]):
            for col_index, pixel in enumerate(row):
                self._draw_pixel(row_index, col_index, pixel)

        for kart in state["karts"]:
            self._draw_kart(kart)

    def _draw_pixel(self, row: int, col: int, pixel: str) -> None:
        """Draw one circuit pixel."""
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size

        color = self.PIXEL_COLORS[pixel]
        outline = "#0b0f16" if pixel != "wall" else "#000000"

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline)

        if pixel == "start":
            self.canvas.create_line(x1 + 3, y1 + 3, x2 - 3, y2 - 3, fill="#fff7ad", width=2)
            self.canvas.create_line(x1 + 3, y2 - 3, x2 - 3, y1 + 3, fill="#a16207", width=1)

    def _draw_kart(self, kart: dict) -> None:
        """Draw one kart as a directional triangle."""
        row, col = kart["position"]
        x = col * self.cell_size + self.cell_size / 2
        y = row * self.cell_size + self.cell_size / 2
        size = self.cell_size * 0.36

        direction = kart["direction"]
        if direction == "north":
            points = (x, y - size, x - size, y + size, x + size, y + size)
        elif direction == "south":
            points = (x, y + size, x - size, y - size, x + size, y - size)
        elif direction == "west":
            points = (x - size, y, x + size, y - size, x + size, y + size)
        else:
            points = (x + size, y, x - size, y - size, x - size, y + size)

        outline = "#ffffff" if kart["is_current"] else "#111827"
        self.canvas.create_polygon(points, fill=kart["color"], outline=outline, width=2)
        self.canvas.create_text(x-3, y, text=str(kart["index"] + 1), fill="#020617", font=("Consolas", 9, "bold"))

        if kart["has_lost"]:
            self.canvas.create_text(x, y, text="X", fill="#ffffff", font=("Consolas", 14, "bold"))

    def _draw_scoreboard(self, state: dict) -> None:
        """Refresh player cards."""
        for widget in self.scoreboard_frame.winfo_children():
            widget.destroy()

        for kart in state["karts"]:
            card_bg = self.PANEL_ALT if kart["is_current"] else self.PANEL
            status = self._kart_status(kart)
            card = tk.Frame(self.scoreboard_frame, bg=card_bg, padx=10, pady=8)
            card.pack(fill="x", pady=4)

            tk.Label(
                card,
                text=kart["name"],
                bg=card_bg,
                fg=kart["color"],
                anchor="w",
                font=("Consolas", 10, "bold"),
            ).pack(fill="x")

            details = (
                f"{status} | Vitesse {kart['speed']} px/tour\n"
                f"Tours {kart['laps_completed']}/{state['total_laps']} | Actions {kart['turns_elapsed']}"
            )
            tk.Label(
                card,
                text=details,
                bg=card_bg,
                fg=self.MUTED,
                justify="left",
                anchor="w",
                font=("Consolas", 9),
            ).pack(fill="x", pady=(4, 0))

    def _kart_status(self, kart: dict) -> str:
        """Return a small status for one kart."""
        if kart["has_won"]:
            return f"Fini en {kart['score']} tours"
        if kart["has_lost"]:
            return "Crash"
        if kart["is_current"]:
            return "A jouer"
        return "En course"

    def _set_action_buttons_state(self, state: str) -> None:
        """Enable or disable all action buttons."""
        for button in self.action_buttons:
            button.config(state=state)

    def _on_new_game(self) -> None:
        """Start a new race from the player-count spinbox and laps_count"""
        try:
            player_count = int(self.player_count_var.get())
            laps_count = int(self.laps_choice_var.get())
        except (tk.TclError, ValueError):
            player_count = 1
            laps_count = 1

        self.controller.new_game(player_count,laps_count)
