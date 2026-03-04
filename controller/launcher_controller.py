"""
Launcher controller for the application.

Responsibilities:
    - Initialize the launcher view (main menu)
    - Handle user interactions
    - Start the selected game
"""

from view.launcher_view import LauncherView
from controller.game_controller import GameController
from model.player import AI, HumanGUI
import random


class LauncherController:
    """
    Controller for the application launcher.
    """

    def __init__(self) -> None:
        """
        Create the launcher controller and its view.
        """
        self.view: LauncherView = LauncherView(self)

    def run(self) -> None:
        """
        Start the graphical application.
        """
        self.view.run()

    def _create_matchsticks_controller(self) -> GameController:
        """
        Create the controller for a matchsticks game.

        Returns:
            A configured GameController.
        """
        ai: AI = AI("AI Bob")
        ai.download("bob_training.json")
        ai.eps = 0.0

        human: HumanGUI = HumanGUI("Me")

        total: int = random.randint(12, 21)

        return GameController(human, ai, total, self.view)

    def on_matchsticks(self) -> None:
        """
        Launch the matchsticks game when the user clicks the card.
        """
        controller: GameController = self._create_matchsticks_controller()
        controller.start()

        game_window = controller.view
        game_window.grab_set()
        game_window.focus_set()