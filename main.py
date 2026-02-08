from model.human import Human
from model.player import Player
from controller.game_controller import GameController

if __name__ == "__main__":
    p1 = Human("Humain")
    p2 = Player("IA Random")  # Player.play() = random 1..3
    GameController(p1, p2, total_matches=21).start()

