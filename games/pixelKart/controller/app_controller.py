from __future__ import annotations

import tkinter as tk

from games.pixelKart.dao import circuit_dao
from games.pixelKart.model.circuit import Circuit
from games.pixelKart.model.kart_factory import KartFactory
from games.pixelKart.dao.Q_table_dao import init_db, SessionLocal
from games.pixelKart.dao.q_table_service import create_agent, load_q_table
from games.pixelKart.model.race import Race
from games.pixelKart.view.circuit_editor import CircuitEditor
from games.pixelKart.view.menu_view import MenuView
from games.pixelKart.view.race_view import RaceView
from games.pixelKart.controller.race_controller import RaceController


class AppController:
    """Control the main PixelKart window and screen changes."""

    KART_COLORS = ["red", "blue", "orange", "purple", "pink", "cyan", "brown", "white"]

    def __init__(self, parent: tk.Misc) -> None:
        """
        Initialize the PixelKart application window.

        Args:
            parent: Parent Tkinter widget.
        """
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("PixelKart")
        self.window.minsize(1000, 650)
        self.window.resizable(True, True)
        self._center_window()

        self.current_view: tk.Widget | None = None
        self.current_controller = None

        self.show_menu()

    def show_menu(self) -> None:
        """Display the PixelKart menu."""
        self._clear_current_view()

        view = MenuView(self.window)
        self.current_view = view
        self.current_controller = None

        view.bind_actions(
            play_callback=self.start_game,
            editor_callback=self.open_circuit_editor,
            refresh_callback=self.refresh_circuits,
        )

        self.refresh_circuits()

    def refresh_circuits(self) -> None:
        """Reload available circuits and update the menu."""
        if not isinstance(self.current_view, MenuView):
            return

        circuit_names = sorted(circuit_dao.get_all().keys())
        self.current_view.set_circuits(circuit_names)

        if circuit_names:
            self.current_view.set_message("")
        else:
            self.current_view.set_message("No circuit available. Create one in the editor.")

    def open_circuit_editor(self) -> None:
        """Open the circuit editor window."""
        CircuitEditor(self.window, callback=self.on_circuit_chosen)

    def on_circuit_chosen(self, circuit_name: str) -> None:
        """
        Select a circuit after using the editor.

        Args:
            circuit_name: Name of the selected circuit.
        """
        self.refresh_circuits()

        if isinstance(self.current_view, MenuView) and circuit_name:
            self.current_view.set_selected_circuit(circuit_name)

    def start_game(self) -> None:
        """Create a race from the menu configuration and display it."""
        if not isinstance(self.current_view, MenuView):
            return

        self.current_view.set_message("")

        try:
            human_players, random_ais, ql_ais, total_laps, circuit_name = (
                self.current_view.get_config()
            )
            total_players = human_players + random_ais + ql_ais

            if total_players <= 0:
                raise ValueError("You must select at least one player.")

            if not circuit_name:
                raise ValueError("You must select a circuit.")

            circuit_dto = circuit_dao.get_by_name(circuit_name)
            if circuit_dto is None:
                raise ValueError(f"Unknown circuit: {circuit_name}")

            circuit = Circuit.from_dto(circuit_dto)
            start_positions = circuit.get_random_start_positions(total_players)

            player_types = (
                ["human"] * human_players
                + ["random"] * random_ais
                + ["ql"] * ql_ais
            )

            shared_q_table = {}

            if ql_ais > 0:
                init_db()

                session = SessionLocal()
                try:
                    db_agent = create_agent(
                        session=session,
                        circuit_name=circuit.name,
                    )

                    temp_kart = KartFactory.create(
                        kart_type="ql",
                        config={
                            "name": "Temporary QL Kart",
                            "color": "red",
                            "position": (0, 0),
                        },
                    )

                    load_q_table(temp_kart, agent_id=db_agent.id, session=session)
                    shared_q_table = temp_kart.q_table.copy()

                finally:
                    session.close()

            karts = []
            counters = {
                "human": 0,
                "random": 0,
                "ql": 0,
            }

            for index, kart_type in enumerate(player_types):
                counters[kart_type] += 1

                if kart_type == "human":
                    name = f"Player {counters[kart_type]}"
                elif kart_type == "random":
                    name = f"Random AI {counters[kart_type]}"
                else:
                    name = f"QLearning AI {counters[kart_type]}"

                config = {
                    "name": name,
                    "color": self.KART_COLORS[index % len(self.KART_COLORS)],
                    "position": start_positions[index],
                    "direction": "EAST",
                }

                if kart_type == "ql":
                    config["q_table"] = shared_q_table
                    config["epsilon"] = 0.0
                    config["alpha"] = 0.2
                    config["gamma"] = 0.95

                kart = KartFactory.create(kart_type=kart_type, config=config)
                karts.append(kart)

            race = Race(circuit=circuit, karts=karts, total_laps=total_laps)
            self.show_race(race)

        except ValueError as error:
            self.current_view.set_message(str(error))

    def show_race(self, race: Race) -> None:
        """
        Display the race screen.

        Args:
            race: Race model to control and display.
        """
        self._clear_current_view()

        view = RaceView(self.window)
        self.current_view = view
        self.current_controller = RaceController(
            race=race,
            view=view,
            on_back_to_menu=self.show_menu,
        )

    def start(self) -> None:
        """Focus the PixelKart window."""
        self.window.grab_set()
        self.window.focus_set()

    def _clear_current_view(self) -> None:
        """Destroy the current screen if one is displayed."""
        if self.current_view is not None:
            self.current_view.destroy()
            self.current_view = None

    def _center_window(self, width: int = 1100, height: int = 700) -> None:
        """
        Center the PixelKart window on the screen.

        Args:
            width: Window width.
            height: Window height.
        """
        self.window.update_idletasks()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.window.geometry(f"{width}x{height}+{x}+{y}")