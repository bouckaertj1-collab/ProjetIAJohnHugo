"""
human.py

Human player for the Tkinter GUI.

Important:
    In a GUI project, we must not use console input(). The human action is
    provided by the controller when the user clicks a button.
"""

from model.player import Player

class HumanGUI(Player):
    """
    Human player for the Tkinter GUI.

    This player does not choose actions through `play()`. Actions come from
    the controller when the user clicks a button.
    """
    
    pass