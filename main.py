"""
Entry point for the matchstick game (Tkinter GUI).
Play Human vs trained Bob (AI).
"""

from model.human import HumanGUI
from model.player import AI,RandomAI
from controller.game_controller import GameController

def main() -> None:
    p1 = HumanGUI("Me")
    bob = AI("Bob Prime 2.0")
    randy = AI("randy")
    alice = AI("Alice")
    random = RandomAI("Merguuuez")

    bob.download("bob_training.json")
    alice.download("alice_training.json")
    randy.download("randy_training.json")
    
    bob.eps = 0.
    alice.eps = 0.
    randy.eps = 0.

    controller = GameController(p1, bob,12)
    controller.start()

if __name__ == "__main__":
    main()
