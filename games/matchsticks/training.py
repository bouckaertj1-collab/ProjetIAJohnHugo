"""
Training and evaluation script for the Matchsticks AI.

This module trains AI players by making them play many automatic games.
After training, the learned value functions are saved into JSON files so
they can be reused by the graphical version of the game.

The AI learns from complete games:
- play_game() runs one full match,
- win()/lose() add the final transition to the AI history,
- train() updates the value function from that history,
- save() saves the trained parameters to JSON.
"""

from pathlib import Path

from game_model import GameModel
from player import AI, Player


BASE_DIR = Path(__file__).resolve().parent

TRAINING_TOTAL_MATCHES = 21
EVALUATION_TOTAL_MATCHES = 12
EPSILON_DECAY_PERIOD = 10

SHORT_TRAINING_GAMES = 1_000
LONG_TRAINING_GAMES = 100_000


def reset_stats(player: Player) -> None:
    """
    Reset only the player's visible game statistics.

    This does not reset the learned value function of an AI. It is useful
    before evaluation, so the displayed win rate only concerns the test games.
    """
    player.nb_wins = 0
    player.nb_loses = 0


def train_if_ai(player: Player) -> None:
    """
    Train the player only if it is an AI.

    Basic Player instances do not have a value function, so they are used as
    random opponents and are ignored by this function.
    """
    if isinstance(player, AI):
        player.train()


def decay_epsilon_if_ai(player: Player) -> None:
    """
    Reduce epsilon only for AI players.

    Epsilon controls exploration. Reducing it over time makes the AI rely more
    on its learned value function as training progresses.
    """
    if isinstance(player, AI):
        player.next_epsilon()


def clear_ai_history(player: Player) -> None:
    """
    Clear temporary learning history for AI players.

    This is useful after evaluation games, because evaluation should measure
    performance without accidentally reusing those transitions for later
    training.
    """
    if isinstance(player, AI):
        player.history.clear()
        player.previous_state = None


def training(
    player1: Player,
    player2: Player,
    nb_games: int,
    epsilon_decay_period: int,
) -> None:
    """
    Train two players over a given number of automatic games.

    The game is played without GUI. After each game, every AI involved updates
    its value function from the transitions collected during that game.

    Args:
        player1: First player, usually an AI.
        player2: Second player, either an AI or a random Player.
        nb_games: Number of games to run.
        epsilon_decay_period: Number of games between epsilon reductions.
    """
    game = GameModel(TRAINING_TOTAL_MATCHES, player1, player2, displayable=False)

    for game_index in range(nb_games):
        game.play_game()

        train_if_ai(player1)
        train_if_ai(player2)

        if (game_index + 1) % epsilon_decay_period == 0:
            decay_epsilon_if_ai(player1)
            decay_epsilon_if_ai(player2)

        game.reset()


def evaluate_ai(ai: AI, opponent: Player, nb_games: int) -> None:
    """
    Evaluate an AI against another player without keeping learning history.

    The AI statistics are reset before evaluation. Its epsilon is temporarily
    set to 0 so the evaluation measures the learned strategy, not random
    exploration.

    Args:
        ai: AI player to evaluate.
        opponent: Opponent used during evaluation.
        nb_games: Number of games to play.
    """
    reset_stats(ai)

    previous_epsilon = ai.eps
    ai.eps = 0.0

    game = GameModel(EVALUATION_TOTAL_MATCHES, ai, opponent, displayable=False)

    for _ in range(nb_games):
        game.play_game()
        game.reset()

    ai.eps = previous_epsilon
    clear_ai_history(ai)
    clear_ai_history(opponent)


def compare_ai(*ais: AI) -> None:
    """
    Print AI statistics and learned values.

    The comparison displays:
    - wins and total games,
    - win rate,
    - learned values for each integer state found in the value functions.
    """
    if not ais:
        raise ValueError("compare_ai() requires at least one AI.")

    print()
    print(f"{'':6}", end="")
    for ai in ais:
        print(f"{ai.name:^15}", end="")
    print()

    print(f"{'Games':6}", end="")
    for ai in ais:
        print(f"{ai.nb_wins}/{ai.nb_games:^13}", end="")
    print()

    print(f"{'Win %':6}", end="")
    for ai in ais:
        win_rate = ai.nb_wins / ai.nb_games * 100 if ai.nb_games else 0.0
        print(f"{win_rate:^15.2f}", end="")
    print()

    print("-" * (6 + len(ais) * 15))

    states = sorted(
        key
        for ai in ais
        for key in ai.v_function
        if isinstance(key, int)
    )

    for state in sorted(set(states)):
        print(f"{state:>5}:", end="")
        for ai in ais:
            print(f"{ai.v_function.get(state, 0.0):^15.3f}", end="")
        print()


def save_training_files(alice: AI, bob: AI, randy: AI) -> None:
    """
    Save trained AI parameters to JSON files.

    These files are later loaded by the GUI launcher, especially Bob's file
    for the human-vs-AI Matchsticks game.
    """
    alice.save(str(BASE_DIR / "alice_training.json"))
    bob.save(str(BASE_DIR / "bob_training.json"))
    randy.save(str(BASE_DIR / "randy_training.json"))

    print()
    print("Training files saved:")
    print(f"- {BASE_DIR / 'alice_training.json'}")
    print(f"- {BASE_DIR / 'bob_training.json'}")
    print(f"- {BASE_DIR / 'randy_training.json'}")


def main() -> None:
    """
    Run the full Matchsticks training process.

    The script trains:
    - Alice against Bob,
    - Randy against a basic random player.

    Bob is then evaluated against a random player, and all trained AI
    parameters are saved to JSON files.
    """
    basic_player = Player("Basic")
    alice = AI("Alice")
    bob = AI("Bob")
    randy = AI("Randy")

    print("Training on 1,000 games...")
    training(alice, bob, SHORT_TRAINING_GAMES, EPSILON_DECAY_PERIOD)
    training(randy, basic_player, SHORT_TRAINING_GAMES, EPSILON_DECAY_PERIOD)

    evaluate_ai(bob, basic_player, SHORT_TRAINING_GAMES)
    compare_ai(alice, bob, randy)

    print()
    print("Training on 100,000 additional games...")
    training(alice, bob, LONG_TRAINING_GAMES, EPSILON_DECAY_PERIOD)
    training(randy, basic_player, LONG_TRAINING_GAMES, EPSILON_DECAY_PERIOD)

    evaluate_ai(bob, basic_player, LONG_TRAINING_GAMES)
    compare_ai(alice, bob, randy)

    save_training_files(alice, bob, randy)


if __name__ == "__main__":
    main()