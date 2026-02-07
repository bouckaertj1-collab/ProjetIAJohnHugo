# human.py
from model.player import Player

class Human(Player):
    """
    Joueur humain.
    Le choix est fait via l'interface graphique (Tkinter),
    puis transmis par le contrôleur.
    """

    def play(self, choice):
        """
        Retourne le choix fait par l'utilisateur.

        Paramètre :
        - choice : int (nombre d'allumettes choisi dans l'interface)

        La validation (1, 2, 3, etc.) sera faite par la classe Game.
        """
        return choice
