from model.game_model import GameModel
from model.player import AI,RandomAI
from random import randint

def training(ai1, ai2, nb_games, nb_epsilon):
    # Train the AIs @ai1 and @ai2 during @nb_games games
    # epsilon decrease every @nb_epsilon games
        training_game = GameModel(randint(12,21), ai1, ai2,)
        for i in range(0, nb_games):
            if i % nb_epsilon == 0:
                if type(ai1) == AI : ai1.next_epsilon()
                if type(ai2) == AI : ai2.next_epsilon()
                

            training_game.play_game()

            if type(ai1)==AI : ai1.train()
            if type(ai2)==AI : ai2.train()

            training_game.reset()

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


alice = AI("Alice")
bob = AI("Bob")
randy = AI("Randy")
randomAi = RandomAI("randomAI")

training(alice, bob, 1000, 10)
training(randy, randomAi, 1000, 10)

bob.nb_wins = 0
bob.nb_loses = 0

test_game = GameModel(12, bob, randomAi)
for _ in range(1000):
    test_game.play_game()
    test_game.reset()


training(alice, bob, 100000, 10)
training(randy,randomAi,100000,10)
compare_ai(alice, bob, randy)
bob.nb_wins = 0
bob.nb_loses = 0

saved_eps = bob.eps
bob.eps = 0.0  # exploitation pure

test_game = GameModel(12, bob, randomAi)
for _ in range(100000):
    test_game.play_game()
    test_game.reset()

bob.eps = saved_eps

compare_ai(alice, bob, randy) 

alice.upload("alice_training.json")
bob.upload("bob_training.json")
randy.upload("randy_training.json")