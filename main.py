"""
Entry point for the matchstick game (Tkinter GUI).
Play Human vs trained Bob (AI).
"""
import random
from model.player import AI, HumanGUI
from controller.game_controller import GameController

if __name__ == "__main__":

    p1 = HumanGUI("Me")
    bob = AI("AI  Bob")
    randy = AI("randy")
    alice = AI("Alice")

    bob.download("bob_training.json")
    alice.download("alice_training.json")
    randy.download("randy_training.json")
    
    bob.eps = 0.
    alice.eps = 0.
    randy.eps = 0.

    controller = GameController(p1, bob, random.randint(12, 21))
    controller.start()
