"""
Training and evaluation utilities for the matches game AIs.

This module provides:
- training(): train two players (AIs and/or basic Player) for a number of games
- compare_ai(): display win rates and learned value functions for AIs

The training protocol matches the assignment requirements:
- epsilon decay every N games (for AI instances only)
- after each game, AI instances update their value function via train()
"""

from typing import Any

from game_model import GameModel
from player import AI, Player


def training(ai1: Player, ai2: Player, nb_games: int, nb_epsilon: int) -> None:
    """
    Train two players for a given number of games.

    If a player is an AI instance, its epsilon is decayed every `nb_epsilon` games
    and its value function is updated after each game using `train()`.

    Args:
        ai1: First player (AI or basic Player).
        ai2: Second player (AI or basic Player).
        nb_games: Number of games to play for training.
        nb_epsilon: Epsilon decay period (in games).
    """
    training_game = GameModel(21, ai1, ai2, displayable=False)

    for i in range(nb_games):
        if i % nb_epsilon == 0:
            if isinstance(ai1, AI):
                ai1.next_epsilon()
            if isinstance(ai2, AI):
                ai2.next_epsilon()

        training_game.play_game()

        if isinstance(ai1, AI):
            ai1.train()
        if isinstance(ai2, AI):
            ai2.train()

        training_game.reset()


def compare_ai(*ais: AI) -> None:
    """
    Print a comparison between AIs.

    The output includes:
    - wins / games
    - win rate percentage
    - learned state values (value function) for integer states

    Args:
        *ais: One or more AI instances to compare.
    """
    if not ais:
        raise ValueError("compare_ai() requires at least one AI.")

    names = f"{'':4}"
    stats1 = f"{'':4}"
    stats2 = f"{'':4}"

    for ai in ais:
        names += f"{ai.name:^15}"
        stats1 += f"{str(ai.nb_wins) + '/' + str(ai.nb_games):^15}"
        stats2 += f"{f'{ai.nb_wins / ai.nb_games * 100:4.4}' + '%':^15}"

    print(names)
    print(stats1)
    print(stats2)
    print(f"{'-' * 4}{'-' * len(ais) * 15}")

    all_v_dict = {key: [ai.v_function.get(key, 0.0) for ai in ais]
                for key in ais[0].v_function.keys()}

    sorted_v = lambda v_dict: sorted(
        filter(lambda x: type(x[0]) == int, v_dict.items())
    )

    for state, values in sorted_v(all_v_dict):
        print(f"{state:2} :", end="")
        for value in values:
            print(f"{value:^15.3f}", end="")
        print()


if __name__ == "__main__":
    basic_player = Player("Basic")
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