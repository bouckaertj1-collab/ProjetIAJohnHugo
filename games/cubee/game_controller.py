class GameController:
    """
    Contrôleur principal du jeu Cubee.
    """
    def __init__(self, model, view=None, ai_agent=None):
        self.model = model
        self.view = view
        self.ai_agent = ai_agent

    def start(self) -> None:
        """Démarre la partie."""
        if self.view is not None:
            self.view.update_view(self.model.get_state_DTO())

        # Si l'IA commence, elle joue immédiatement
        if self.ai_agent is not None and self.model.player_turn == self.ai_agent.player_id:
            self.handle_ai_move()

    def reset(self) -> None:
        """Réinitialise la partie."""
        self.model.reset()

        if self.view is not None:
            self.view.reset()
            self.view.update_view(self.model.get_state_DTO())

        # Si l'IA commence après reset, elle joue immédiatement
        if self.ai_agent is not None and self.model.player_turn == self.ai_agent.player_id:
            self.handle_ai_move()

    def handle_move(self, move: str) -> bool:
        success = self.model.step(move)

        if self.view is not None:
            self.view.update_view(self.model.get_state_DTO())

        if not success:
            return False

        if self.model.is_game_over:
            self.handle_end_game()
            return True

        # Si après le coup humain c'est le tour de l'IA, elle joue
        if self.ai_agent is not None and self.model.player_turn == self.ai_agent.player_id:
            self.handle_ai_move()

        return True

    def handle_ai_move(self) -> bool:
        if self.ai_agent is None:
            return False

        if self.model.is_game_over:
            return False

        if self.model.player_turn != self.ai_agent.player_id:
            return False

        move = self.ai_agent.choose_action(self.model)

        if move is None:
            return False

        success = self.model.step(move)

        if self.view is not None:
            self.view.update_view(self.model.get_state_DTO())
        
        if self.model.is_game_over:
            self.handle_end_game()

        return success

    def handle_end_game(self):
        """Informe la vue que la partie est terminée."""
        if self.view is not None:
            self.view.end_game(self.get_status_message(), self.model.get_state_DTO())

    def get_status_message(self) -> str:
        """Retourne un message décrivant l'état courant du jeu."""
        if self.model.is_game_over:
            if self.model.winner is None:
                return f"Match nul : {self.model.score[0]} - {self.model.score[1]}"
            return f"{self.model.winner.name} gagne : {self.model.score[0]} - {self.model.score[1]}"

        return f"Tour du joueur {self.model.player_turn}"

    def get_state_DTO(self) -> dict:
        """Retourne le DTO du modèle."""
        return self.model.get_state_DTO()
    