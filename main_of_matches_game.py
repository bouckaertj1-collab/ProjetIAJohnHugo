"""
Entry point for the matchstick game (Tkinter GUI).
Play Human vs trained Bob (AI).
"""
import random
from model.player import AI, HumanGUI,RandomAI
from controller.game_controller import GameController

""" 
Add these args after refactored hub and gameView ===> player1:HumanGUI|AI,player2:HumanGUI|AI,ai_difficulty,trainingAi_or_playing:bool
Implement functions to :
    - train ais
    - choose ai difficulty
    - start a game human player vs human player 
"""

def start_match_stick(parent_window):
    ai = AI("AI")
    random_ai = RandomAI("random AI")
    human_player = HumanGUI("Hugo")
    controller =  GameController(human_player,ai,12,parent_window)
    controller.start()
    game_window = controller.view
    game_window.grab_set()
    game_window.focus_set()

def settings():
    pass


