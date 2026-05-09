from __future__ import annotations

from collections.abc import Callable

from games.PixelKart.model.race import Race
from games.PixelKart.view.race_view import RaceView
from games.PixelKart.dao.q_table_service import *
from games.PixelKart.dao.Q_table_dao import *
from games.PixelKart.model.kart import QLearningKart,RandomAIKart


class RaceController:
    """Coordinate the race model and the race view."""

    def __init__(
        self,
        race: Race,
        view: RaceView,
        on_back_to_menu: Callable[[], None] | None = None,
        agent_id: int | None = None,
        exploit_only: bool = False
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
        self.save_counter = 0
        self.agent_id = agent_id 
        
        self.q_learning_karts = [
            kart for kart in self.race.karts if isinstance(kart, QLearningKart)
        ]

        if exploit_only:
            for kart in self.q_learning_karts:
                kart.epsilon = 0.0

        self.view.bind_action(self.handle_turn)
        self.view.bind_back_to_menu(self.back_to_menu)
        self.view.set_circuit(self.race.circuit.to_dto()["grid"])
        self.refresh_view()

        if self.race.get_current_kart().is_ai:
            self.view.after(0, self.handle_turn)

    def _save_q_learning(self):

        if not self.q_learning_karts: 
            return
        session = SessionLocal()
        try:   
            save_q_table(self.q_learning_karts[0], session, self.agent_id)
            session.commit()
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            session.rollback()
        finally:
            session.close()

    def handle_turn(self, action: str | None = None) -> None:
        """"""
        if self.race.finished:
            self.refresh_view()
            self._save_q_learning()
            return

        kart = self.race.get_current_kart()

        if kart.is_ai:
            self.play_ai_turn()
        else:
            if action is None:
                return
            self.player_human_turn(action)
            self.play_ai_turn()
            
        if self.race.finished:
            self.refresh_view()
            self._save_q_learning()
            return    
        
        self.refresh_view()
        

    def back_to_menu(self) -> None:
        """Ask the parent controller to go back to the menu."""
        if self.on_back_to_menu is not None:
            self.on_back_to_menu()

    def play_ai_turn(self):
            """"""
            
            max_steps = 2000
            steps = 0
            while not self.race.finished and isinstance(self.race.get_current_kart(),(QLearningKart,RandomAIKart)) and steps < max_steps:
                
                kart = self.race.get_current_kart()

                print(f"[DEBUG] Q-table size: {len(kart.q_table)}") 

                if isinstance(kart, QLearningKart):
                    state = kart.get_state(self.race.circuit)

                    old_position = kart.position

                    action = kart.choose_action(state,self.race.circuit)
                    
                    self.race.step(action)

                    """  
                    crash = not kart.is_alive
                    finished = kart.has_finished
                    current_position = kart.position

                    reward = kart.compute_reward(crash, finished, old_position, current_position,self.race.circuit,action)
                    
                    if action == "pass":
                        reward -= 10
                    
                    next_state = None if crash or finished else kart.get_state(self.race.circuit)

                    kart.learn(state, action, reward, next_state) 
                    """
                
                else:
                    action = kart.choose_action()
                    self.race.step(action)
                steps +=1

                if steps >= max_steps:
                    self.race.finished = True
                    self.race.winner_name = None      

                    alive_karts = [kart for kart in self.race.karts if kart.is_alive]
                    if alive_karts:
                        self.race.winner_name = max(alive_karts, key=lambda k: k.laps_done).name
                    else:
                        self.race.winner_name = None
            return

    def player_human_turn(self,action):
        self.race.step(action)
    
    def refresh_view(self) -> None:
        """Refresh the race view from the current model state."""
        self.view.update_view(
            race_dto=self.race.to_dto(),
            kart_dtos=[kart.to_dto() for kart in self.race.karts],
            current_kart_name=self.race.get_current_kart().name,
        )
