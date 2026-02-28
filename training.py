from model.game_model import GameModel
from model.player import AI,RandomAI
from random import randint

def training(ai1, ai2, nb_games, nb_epsilon):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games
    training_game = GameModel(12, ai1, ai2, displayable = False)
    for i in range(0, nb_games):
        if i % nb_epsilon == 0:
            if type(ai1)==AI : ai1.next_epsilon()
            if type(ai2)==AI : ai2.next_epsilon()

        training_game.play_game()
        if type(ai1)==AI : ai1.train()
        if type(ai2)==AI : ai2.train()

        training_game.reset()

def training2(ai1, ai2, nb_games, nb_epsilon):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games

    for i in range(nb_games):
        if i % nb_epsilon == 0:
            if type(ai1) == AI: ai1.next_epsilon()
            if type(ai2) == AI: ai2.next_epsilon()

        training_game = GameModel(randint(12, 21), ai1, ai2)
        training_game.play_game()

        if type(ai1) == AI: ai1.train()
        if type(ai2) == AI: ai2.train()

def compare_ai(*ais):
    # Print a comparison between the @ais
        names = f"{'':4}"
        stats1 = f"{'':4}"
        stats2 = f"{'':4}"

        for ai in ais :
            names += f"{ai.name:^15}"
            stats1 += f"{str(ai.nb_wins)+'/'+str(ai.nb_games):^15}"
            stats2 += f"{f'{ai.nb_wins/ai.nb_games*100:4.4}'+'%':^15}"

        print(names)
        print(stats1)
        print(stats2)
        print(f"{'-'*4}{'-'*len(ais)*15}")

        all_v_dict = {key : [ai.v_function.get(key,0) for ai in ais] for key in ais[0].v_function.keys()}
        sorted_v = lambda v_dict : sorted(filter(lambda x : type(x[0])==int ,v_dict.items()))
        for state, values in sorted_v(all_v_dict):
            print(f"{state:2} :", end='')
            for value in values:
                    print(f"{value:^15.3f}", end='')
            print()

if __name__ == "__main__":
    basic_player = RandomAI("Basic")
    alice = AI("Alice")
    bob = AI("Bob")
    randy = AI("Randy")

    training(alice, bob, 1000, 10)
    training(randy, basic_player, 1000, 10)

    bob.nb_wins = 0
    bob.nb_loses = 0

    test_game = GameModel(12, bob, basic_player, displayable=False)
    for _ in range(1000):
        test_game.play_game()
        test_game.reset()

    compare_ai(alice, bob, randy)

    training(alice, bob, 100000, 10)
    training(randy, basic_player, 100000, 10)

    bob.nb_wins = 0
    bob.nb_loses = 0

    test_game = GameModel(12, bob, basic_player, displayable=False)
    for _ in range(100000):
        test_game.play_game()
        test_game.reset()

    compare_ai(alice, bob, randy)