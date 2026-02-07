from model.player import Player

class Human(Player):
    """
    Joueur humain pour Tkinter.
    Le choix est fourni par la Vue/Contrôleur via l'attribut next_action.
    """

    def __init__(self, name, game=None):
        super().__init__(name, game)
        self.next_action = None  # la Vue/Contrôleur mettra 1/2/3 ici

    def play(self):
        """
        Retourne le choix de l'utilisateur.
        En Tkinter, on ne demande pas via input(); on récupère ce que l'UI a mis.
        """
        return self.next_action
