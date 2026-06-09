import json
from pathlib import Path

from games.cubee.game_model import GameModel
from games.cubee.player import QLearningAgent


FINAL_ALPHA = 0.40
FINAL_GAMMA = 0.80
FINAL_BOARD_SIZE = 5
FINAL_SELF_PLAY_GAMES = 500_000

RESULTS_DIR = Path(__file__).resolve().parent / "training_results"
FINAL_QTABLE_PATH = Path(__file__).resolve().parent / "cubee_trained_qtableB.json"


def play_full_game(model: GameModel) -> None:
    """
    Play a complete game without any graphical interface.

    The function repeatedly asks the current player to play until the
    model reaches a terminal state.
    """
    while not model.is_game_over:
        model.current_player.play()


def train_self_play(alpha: float, gamma: float, size: int, games: int) -> dict:
    """
    Train two Q-learning agents against each other with a shared Q-table.

    The two agents learn simultaneously and enrich the same final Q-table,
    which is saved under a generic filename for later use in the launcher.

    Returns:
        A dictionary describing the final self-play training run.
    """
    qtable_path = FINAL_QTABLE_PATH

    agent1 = QLearningAgent("Q-Bot A", (0, 0))
    agent2 = QLearningAgent("Q-Bot B", (size - 1, size - 1))

    shared_q_table = {}

    for agent in (agent1, agent2):
        agent.alpha = alpha
        agent.gamma = gamma
        agent.epsilon = 0.9
        agent.q_table = shared_q_table

        agent.configure_learning(
            learning_enabled=True,
            auto_save=False,
            auto_decay=True,
            qtable_filename=str(qtable_path),
        )

    model = GameModel(agent1, agent2, size=size)

    print("Self-play epsilon start:", agent1.epsilon, agent2.epsilon)

    for game_index in range(games):
        play_full_game(model)

        if game_index < games - 1:
            model.reset()

        if (game_index + 1) % 10_000 == 0:
            print(f"{game_index + 1}/{games} games completed")

    agent1.save()

    return {
        "alpha": alpha,
        "gamma": gamma,
        "board_size": size,
        "train_games": games,
        "shared_qtable": str(qtable_path),
        "final_epsilon_agent1": agent1.epsilon,
        "final_epsilon_agent2": agent2.epsilon,
        "qtable_states": len(shared_q_table),
        "qtable_actions": sum(len(actions) for actions in shared_q_table.values()),
    }


def main() -> None:
    """
    Run the final Cubee self-play training.

    Parameter tuning is handled separately in parameter_tuning.py.
    This file only trains the final Q-table used by the launcher.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    training_result = train_self_play(
        alpha=FINAL_ALPHA,
        gamma=FINAL_GAMMA,
        size=FINAL_BOARD_SIZE,
        games=FINAL_SELF_PLAY_GAMES,
    )

    summary_path = RESULTS_DIR / "training_summary.json"
    summary_path.write_text(
        json.dumps(training_result, indent=4),
        encoding="utf-8",
    )

    print(f"\nFinal Q-table saved to: {FINAL_QTABLE_PATH}")
    print(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()