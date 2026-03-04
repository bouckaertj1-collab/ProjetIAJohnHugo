"""
Entry point for the matchstick game (Tkinter GUI).
Play Human vs trained Bob (AI).
"""
from model.player import AI, HumanGUI

from controller.game_controller import GameController
def start_match_stick(parent_window):
    ai = AI("AI")
    ai.download("bob_training.json")
    ai.eps = 0.0
    human_player = HumanGUI("Hugo")
    controller =  GameController(human_player,ai,12,parent_window)
    controller.start()
    game_window = controller.view
    game_window.grab_set()
    game_window.focus_set()

def settings():
    pass




