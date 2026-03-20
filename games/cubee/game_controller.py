class GameController:
    """
    Contrôleur principal du jeu Cubee.
    """

    def __init__(self, model, view=None):
        self.model = model
        self.view = view

    def start(self) -> None:
        if self.view:
            self.view.update_view(self.model.get_state_DTO())

        self.handle_ai_move()

    def reset(self) -> None:
        self.model.reset()

        if self.view:
            self.view.reset()
            self.view.update_view(self.model.get_state_DTO())

        self.handle_ai_move()

    def handle_move(self, move: str) -> bool:
        success = self.model.step(move)

        if self.view:
            self.view.update_view(self.model.get_state_DTO())

        if not success:
            return False

        if self.model.is_game_over:
            self.handle_end_game()
            return True

        self.handle_ai_move()
        return True

    def handle_ai_move(self) -> bool:
        current_player = self.model.get_current_player()

        if not current_player.is_ai():
            return False

        move = current_player.play(self.model)
        if move is None:
            return False

        success = self.model.step(move)

        if self.view:
            self.view.update_view(self.model.get_state_DTO())

        if success and self.model.is_game_over:
            self.handle_end_game()

        return success
    
    def handle_cell_click(self, row: int, col: int) -> bool:
        state = self.model.get_state_DTO()

        if state["player_turn"] == 1:
            current_row, current_col = state["pos_p1"]
        else:
            current_row, current_col = state["pos_p2"]

        moves = {
            (-1, 0): "up",
            (1, 0): "down",
            (0, -1): "left",
            (0, 1): "right",
        }

        move = moves.get((row - current_row, col - current_col))
        if move is None:
            return False

        return self.handle_move(move)

    def handle_end_game(self) -> None:
        if self.view:
            self.view.end_game(
                self.get_status_message(),
                self.model.get_state_DTO()
            )
    
    def get_status_message(self) -> str:
        p1 = self.model.player1
        p2 = self.model.player2

        if self.model.is_game_over:
            if self.model.winner is None:
                result = f"Draw: {self.model.score[0]} - {self.model.score[1]}"
            else:
                result = f"{self.model.winner.name} wins: {self.model.score[0]} - {self.model.score[1]}"
        else:
            result = f"Player {self.model.player_turn}'s turn"

        stats = (
            f"\n\n{p1.name} - Games: {p1.nb_game}, W: {p1.nb_win}, L: {p1.nb_lose}, D: {p1.nb_draw}"
            f"\n{p2.name} - Games: {p2.nb_game}, W: {p2.nb_win}, L: {p2.nb_lose}, D: {p2.nb_draw}"
        )

        return result + stats

    def get_state_DTO(self) -> dict:
        return self.model.get_state_DTO()