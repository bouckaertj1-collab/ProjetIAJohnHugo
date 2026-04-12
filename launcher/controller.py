"""
Launcher controller for the application.

Responsibilities:
    - Initialize the launcher view (main menu)
    - Handle user interactions
    - Start the selected game
"""

from launcher.view import LauncherView
from games.matchsticks.game_controller import GameController
from games.matchsticks.player import AI, HumanGUI
from games.cubee.game_model import GameModel as CubeeModel
from games.cubee.game_controller import GameController as CubeeController
from games.cubee.game_view import GameView as CubeeView
from games.cubee.player import Player, QLearningAgent , RandomAgent
from games.PixelKart.game_controller import GameController as PixelKartController
from games.PixelKart.game_model.game_model import GameModel as PixelKartModel
from games.PixelKart.game_view import GameView as PixelKartView
import random
from games.PixelKart.__init__ import __all__


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
        ai.download("games/matchsticks/bob_training.json")
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

    def _create_cubee_controller(self) -> CubeeController:
        """
        Create the controller for a Cubee game.

        Returns:
            A configured CubeeController.
        """
        size: int = 5

        player1: Player = Player("Human", (0, 0))
        player2: QLearningAgent = QLearningAgent("Q-Bot", (size - 1, size - 1))

        player2.download()
        player2.epsilon = 0.05

        model: CubeeModel = CubeeModel(player1, player2, size=size)
        controller: CubeeController = CubeeController(model)

        return controller

    def on_cubee(self) -> None:
        """
        Launch the Cubee game when the user clicks the card.
        """
        controller: CubeeController = self._create_cubee_controller()
        view: CubeeView = CubeeView(self.view, controller, size=controller.model.size)

        controller.view = view
        controller.start()

        view.grab_set()
        view.focus_set()

    def _create_pixelkart_controller(self) -> PixelKartController:
        """
        Create the controller for a PixelKart game.

        Returns:
            A configured PixelKartController.
        """
        model = PixelKartModel()
        return PixelKartController(model)

    def on_pixelkart(self) -> None:
        """
        Launch PixelKart when the user clicks the card.
        """
        controller = self._create_pixelkart_controller()
        view = PixelKartView(self.view, controller)

        controller.view = view
        controller.start()

        view.grab_set()
        view.focus_set()
