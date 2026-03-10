from game_model import GameModel
from game_view import GameView
from game_controller import GameController
from player import Player, RandomAgent

def main() -> None:
    size = 5

    player1 = Player("Human", (0, 0))
    player2 = RandomAgent("Random Randy", (size - 1, size - 1))

    model = GameModel(player1, player2, size=size)
    controller = GameController(model)
    view = GameView(controller, size=model.size)

    controller.view = view
    controller.start()
    view.run()

if __name__ == "__main__":
    main()