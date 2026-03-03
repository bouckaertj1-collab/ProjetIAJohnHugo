"""
Entry point for the matchstick game (Tkinter GUI).
Play Human vs trained Bob (AI).
"""
import random
from model.player import AI, HumanGUI
from controller.game_controller import GameController

""" 
Add these args after refactored hub and gameView ===> player1:HumanGUI|AI,player2:HumanGUI|AI,ai_difficulty,trainingAi_or_playing:bool
Implement functions to :
    - train ais
    - choose ai difficulty
    - start a game human player vs human player 
"""

def start_match_stick(parent):
    ai = AI("AI")
    random_ai = random_ai("random AI")
    human_player = HumanGUI("Hugo")
    controller =  GameController(ai,human_player,12)
    controller.start()


