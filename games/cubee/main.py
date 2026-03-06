from game_model import GameModel
from game_controller import GameController
from game_view import GameView
from ai.random_agent import RandomAgent

def main():

    model = GameModel("Human", "AI", size=5)

    ai_agent = RandomAgent(player_id=2)

    controller = GameController(model, ai_agent=ai_agent)

    view = GameView(controller, size=model.size)

    controller.view = view
    controller.start()

    view.run()

if __name__ == "__main__":
    main()