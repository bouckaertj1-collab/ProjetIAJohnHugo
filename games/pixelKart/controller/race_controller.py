from __future__ import annotations

from collections.abc import Callable

from games.pixelKart.model.race import Race
from games.pixelKart.view.race_view import RaceView
from games.pixelKart.dao.q_table_service import save_q_table
from games.pixelKart.dao.Q_table_dao import SessionLocal
from sqlalchemy.orm import Session
from games.pixelKart.model.kart import QLearningKart


class RaceController:
    """Coordinate the race model and race view."""

    def __init__(
        self,
        race: Race,
        view: RaceView,
        on_back_to_menu: Callable[[], None] | None = None,
        session: Session | None = None, 
        agents: list | None = None, 
    ) -> None:
        """
        Initialize the race controller.

        Args:
            race: Race model to control.
            view: Race view to update.
            on_back_to_menu: Callback used to return to the menu.
        """
        self.race = race
        self.view = view
        self.on_back_to_menu = on_back_to_menu
        self.ai_turns_without_human = 0
        self.max_ai_turns_without_human = 2000
        self.session = session
        self.agents = agents  

        self.view.bind_action(self.on_action_selected)
        self.view.bind_back_to_menu(self.back_to_menu)
        self.view.set_circuit(self.race.circuit.to_dto()["grid"])

        self.refresh_view()
        self.schedule_ai_turn_if_needed()

    def on_action_selected(self, action: str) -> None:
        """
        Play a human action selected in the view.

        Args:
            action: Action selected by the human player.
        """
        if self.race.finished:
            self.refresh_view()
            return

        current_kart = self.race.get_current_kart()

        if current_kart.is_ai or not current_kart.is_alive or current_kart.has_finished:
            return

        self.ai_turns_without_human = 0

        self.race.play_current_turn(action)
        self.refresh_view()

        self.schedule_ai_turn_if_needed()

    def back_to_menu(self) -> None:
        """Return to the PixelKart menu."""
        if self.session is not None and self.agents is not None:
            for agent, kart in zip(self.agents, self.race.karts):
                if isinstance(kart, QLearningKart):
                    save_q_table(kart, self.session, agent.id)
            self.session.close()
        if self.on_back_to_menu is not None:
            self.on_back_to_menu()

    def schedule_ai_turn_if_needed(self) -> None:
        """Schedule an AI turn when the current kart is AI-controlled."""
        if self.race.finished:
            self.refresh_view()
            return

        current_kart = self.race.get_current_kart()

        if not current_kart.is_alive or current_kart.has_finished:
            self.race.next_player()
            self.race.check_end_game()
            self.refresh_view()
            self.schedule_ai_turn_if_needed()
            return

        if current_kart.is_ai:
            self.view.after(300, self.play_one_ai_turn)
        else:
            self.refresh_view()

    def play_one_ai_turn(self) -> None:
        """Play one AI turn and schedule the next turn if needed."""
        if self.race.finished:
            self.refresh_view()
            return

        current_kart = self.race.get_current_kart()

        if not current_kart.is_alive or current_kart.has_finished:
            self.race.next_player()
            self.race.check_end_game()
            self.refresh_view()
            self.schedule_ai_turn_if_needed()
            return

        if not current_kart.is_ai:
            self.refresh_view()
            return

        self.ai_turns_without_human += 1

        if self.ai_turns_without_human >= self.max_ai_turns_without_human:
            self.race.finished = True
            self.race.winner_name = None
            self.refresh_view()
            return
        
        if isinstance(current_kart, QLearningKart):
            old_state = current_kart.get_state(self.race.circuit)
            old_position = current_kart.position
            old_laps = current_kart.laps_done

        action =current_kart.choose_action(old_state,self.race.get_allowed_actions(current_kart))

        self.race.play_current_turn(action) 

        if isinstance(current_kart, QLearningKart):

            new_state = current_kart.get_state(self.race.circuit) if current_kart.is_alive else None
            completed_lap = current_kart.laps_done > old_laps
            reward = current_kart.compute_reward(
                has_crashed=not current_kart.is_alive,
                has_finished=current_kart.has_finished,
                old_position=old_position,
                new_position=current_kart.position,
                circuit=self.race.circuit,
                completed_lap=completed_lap,
            )

            
            current_kart.learn(old_state, action, reward, new_state)

        self.refresh_view()
        self.schedule_ai_turn_if_needed()

    def refresh_view(self) -> None:
        """Update the view from the current race state."""
        self.view.update_view(
            race_dto=self.race.to_dto(),
            kart_dtos=[kart.to_dto() for kart in self.race.karts],
            current_kart_name=self.race.get_current_kart().name,
        )