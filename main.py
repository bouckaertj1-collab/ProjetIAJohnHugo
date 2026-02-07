from model.player import Player
from model.game import Game

if __name__ == "__main__":
    p1 = Player("Joueur 1", 2)
    p2 = Player("Joueur 2")

    game = Game(nb=21, player1=p1, player2=p2, displayable=True)
    winner = game.play()

    for i in range(10):
        game.play()

    print("Résultats après 10 parties :")
    print(p1)
    print(p2)

    print("\n--- FIN ---")
   
