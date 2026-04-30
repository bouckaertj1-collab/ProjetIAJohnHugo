from __future__ import annotations

from collections.abc import Callable

from games.PixelKart.model.race import Race
from games.PixelKart.view.race_view import RaceView
from games.PixelKart.dao.q_table_service import *
from games.PixelKart.dao.q_table_dao import *
from games.PixelKart.model.kart import QLearningKart
from games.PixelKart.dao.q_table_dao import SessionLocal



class RaceController:
    """Coordinate the race model and the race view."""

    def __init__(
        self,
        race: Race,
        view: RaceView,
        on_back_to_menu: Callable[[], None] | None = None,
    ) -> None:
        """
        Initialize the race controller.

        Args:
            race: Race model instance.
            view: Race view instance.
            on_back_to_menu: Callback used to go back to the menu.
        """
        self.race = race
        self.view = view
        self.on_back_to_menu = on_back_to_menu
        

        self.q_learning_karts = [
            kart for kart in self.race.karts if isinstance(kart, QLearningKart)
        ]

        if self.q_learning_karts:
            self._init_q_learning()

        self.view.bind_action(self.handle_turn)
        self.view.bind_back_to_menu(self.back_to_menu)
        self.view.set_circuit(self.race.circuit.to_dto()["grid"])

        self.refresh_view()

    def _init_q_learning(self):
        self.session = SessionLocal()

        db_agent = create_agent(self.session)
        self.agent_id = db_agent.id

        for kart in self.q_learning_karts:
            load_q_table(kart,self.agent_id,self.session)

    def _save_q_learning(self):
        for kart in self.q_learning_karts:
            save_q_table(kart,self.agent_id,self.session)

    def handle_turn(self, action: str | None = None) -> None:
        """"""
        if self.race.finished:
            self._save_q_learning()
            return

        kart = self.race.get_current_kart()

        if kart.is_ai:
            self._play_ai_turn()
        else:
            if action is None:
                return
            self.player_human_turn(action)
        
        self.refresh_view()

        if not self.race.finished and self.race.get_current_kart().is_ai:
            self.view.after(50, self.handle_turn)

    def back_to_menu(self) -> None:
        """Ask the parent controller to go back to the menu."""
        if self.on_back_to_menu is not None:
            self.on_back_to_menu()

    def _play_ai_turn(self):

            kart = self.race.get_current_kart()
            
            if isinstance(kart, QLearningKart):
                state = kart.get_state(self.race.circuit)

                old_speed = kart.speed

                action = kart.choose_action(state)
                self.race.step(action)

                crash = not kart.is_alive
                finished = kart.has_finished
                current_speed = kart.speed

                reward = kart.compute_reward(crash, finished, old_speed, current_speed)

                next_state = None if crash or finished else kart.get_state(self.race.circuit)

                kart.learn(state, action, reward, next_state)
                
            else:
                action = kart.choose_action()
                self.race.step(action)

    def player_human_turn(self,action):
        self.race.step(action)
    
    def _schedule_next_if_ai(self):
        if not self.race.finished:
            next_kart = self.race.get_current_kart()

            if next_kart.is_ai:
                self.view.after(0, self.handle_turn)

    def refresh_view(self) -> None:
        """Refresh the race view from the current model state."""
        self.view.update_view(
            race_dto=self.race.to_dto(),
            kart_dtos=[kart.to_dto() for kart in self.race.karts],
            current_kart_name=self.race.get_current_kart().name,
        )
