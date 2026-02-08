# controller/game_controller.py
from model.game_model import GameModel
from model.human import Human

from view.game_view import GameView

class GameController:
    def __init__(self, p1, p2, total_matches):
        # au moins un humain, sinon l'UI n'a pas de sens (consigne)
        if not isinstance(p1, Human) and not isinstance(p2, Human):
            raise Exception("Au moins un joueur doit être un Human pour jouer via l'interface.")

        self.model = GameModel(total_matches, p1, p2, displayable=False)
        self.view = GameView(self)

        # Si l'IA commence, il faut la faire jouer tout de suite (consigne H)
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()
            self.view.update_view()

    def start(self):
        self.view.mainloop()

    def get_nb_matches(self):
        return self.model.nb

    def get_status_message(self):
        if self.model.is_game_over():
            winner = self.model.get_winner()
            loser = self.model.get_loser()
            return f"Fin ! {winner.name} gagne — {loser.name} a pris la dernière."
        else:
            return f"Tour de: {self.model.get_current_player().name}"

    def reset_game(self):
        self.model.reset()
        self.view.reset()

        # si l'IA commence après reset, la faire jouer
        if not isinstance(self.model.get_current_player(), Human):
            self.handle_ai_move()
            self.view.update_view()

    def handle_human_move(self, taken):
        # Ce n'est pas le tour de l'humain -> on ignore
        if not isinstance(self.model.get_current_player(), Human):
            return

        # Jouer le coup humain
        try:
            self.model.step(taken)
        except ValueError:
            return

        # Si fin -> gérer fin
        if self.model.is_game_over():
            self.handle_end_game()
            self.view.update_view()
            return

        # Sinon joueur suivant
        self.model.switch_player()

        # Mettre à jour la vue pour bien voir que c'est au tour de l'IA
        self.view.update_view()

        # Si c'est une IA, la faire jouer APRES un petit délai
        if not isinstance(self.model.get_current_player(), Human):
            self.view.after(400, self.handle_ai_move)


    def handle_ai_move(self):
        ai = self.model.get_current_player()

        # Choisir une action valide
        action = ai.play()
        while action > self.model.nb:
            action = ai.play()

        self.model.step(action)

        if self.model.is_game_over():
            self.handle_end_game()
            self.view.update_view()
            return

        self.model.switch_player()
        self.view.update_view()



    def handle_end_game(self):
        winner = self.model.get_winner()
        loser = self.model.get_loser()
        winner.win()
        loser.lose()
        # l'affichage de fin se fera via view.update_view() -> end_game()
