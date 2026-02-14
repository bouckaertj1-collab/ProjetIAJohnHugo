"""
Entry point for the matchstick game (Tkinter GUI).
"""

from model.human import HumanGUI
from model.player import RandomAI
from controller.game_controller import GameController


def main() -> None:
    """
    Start the application.

    Postconditions:
        - Creates players and controller
        - Starts the Tkinter event loop
    """
    p1 = HumanGUI("Me")
    p2 = RandomAI("Bot")

    controller = GameController(p1, p2, total_matches=42)
    controller.start()


if __name__ == "__main__":
    main()
