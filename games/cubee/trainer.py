from __future__ import annotations

import json
from pathlib import Path

from games.cubee.game_model import GameModel
from games.cubee.player import QLearningAgent, RandomAgent

ALPHAS = [0.10, 0.13, 0.17, 0.20]
GAMMAS = [0.20, 0.40, 0.60, 0.80]
TRAIN_GAMES = 60_000
EVAL_GAMES = 1000
SMALL_BOARD_SIZE = 3
LARGE_BOARD_SIZE = 5
SELF_PLAY_GAMES = 500_000
RESULTS_DIR = Path(__file__).resolve().parent / "training_results"
QTABLES_DIR = RESULTS_DIR / "qtables"


def play_full_game(model: GameModel) -> None:
    """Run a full game without any graphical view."""
    while not model.is_game_over:
        success = model.current_player.play()
        if not success:
            raise RuntimeError(f"Illegal move produced by {model.current_player.name}")


def train_vs_random(alpha: float, gamma: float, size: int, train_games: int) -> str:
    """Train one Q-learning agent against a random opponent."""
    qtable_path = QTABLES_DIR / f"random_size{size}_a{alpha:.2f}_g{gamma:.2f}.json"

    random_agent = RandomAgent("Random", (0, 0))
    learner = QLearningAgent("Q-Bot", (size - 1, size - 1))
    learner.alpha = alpha
    learner.gamma = gamma
    learner.epsilon = 0.9
    learner.configure_runtime(
        learning_enabled=True,
        auto_save=False,
        auto_decay=True,
        qtable_filename=str(qtable_path),
    )

    model = GameModel(random_agent, learner, size=size)

    print("Training epsilon start:", learner.epsilon)

    for game_index in range(train_games):
        play_full_game(model)
        if game_index < train_games - 1:
            model.reset()

    learner.upload()
    return str(qtable_path)


def evaluate_vs_random(
    qtable_path: str,
    alpha: float,
    gamma: float,
    size: int,
    eval_games: int,
) -> dict:
    """Evaluate a trained agent against a random opponent."""
    random_agent = RandomAgent("Random", (0, 0))
    evaluator = QLearningAgent("Q-Bot", (size - 1, size - 1))
    evaluator.alpha = alpha
    evaluator.gamma = gamma
    evaluator.configure_runtime(
        learning_enabled=False,
        auto_save=False,
        auto_decay=False,
        qtable_filename=qtable_path,
    )
    evaluator.download(qtable_path)
    evaluator.epsilon = 0.0

    model = GameModel(random_agent, evaluator, size=size)

    wins = 0
    losses = 0
    draws = 0

    for game_index in range(eval_games):
        play_full_game(model)

        if model.winner is evaluator:
            wins += 1
        elif model.winner is random_agent:
            losses += 1
        else:
            draws += 1

        if game_index < eval_games - 1:
            model.reset()

    return {
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": wins / eval_games,
    }


def sweep_parameters() -> tuple[dict, list[dict]]:
    """Try several alpha/gamma pairs on a small board."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    QTABLES_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    for alpha in ALPHAS:
        for gamma in GAMMAS:
            print(f"Training alpha={alpha:.2f}, gamma={gamma:.2f}...")
            qtable_path = train_vs_random(alpha, gamma, SMALL_BOARD_SIZE, TRAIN_GAMES)
            evaluation = evaluate_vs_random(qtable_path, alpha, gamma, SMALL_BOARD_SIZE, EVAL_GAMES)

            result = {
                "alpha": alpha,
                "gamma": gamma,
                "board_size": SMALL_BOARD_SIZE,
                "train_games": TRAIN_GAMES,
                "eval_games": EVAL_GAMES,
                "qtable_path": qtable_path,
                **evaluation,
            }
            results.append(result)
            print(
                " -> "
                f"wins={evaluation['wins']}, "
                f"losses={evaluation['losses']}, "
                f"draws={evaluation['draws']}, "
                f"win_rate={evaluation['win_rate']:.3f}"
            )

    best_result = max(results, key=lambda item: (item["win_rate"], -item["losses"]))
    return best_result, results


def train_self_play(alpha: float, gamma: float, size: int, games: int) -> dict:
    """Train two Q-learning agents with a shared Q-table."""
    qtable_path = QTABLES_DIR / f"selfplay_shared_size{size}_a{alpha:.2f}_g{gamma:.2f}.json"

    agent1 = QLearningAgent("Q-Bot A", (0, 0))
    agent2 = QLearningAgent("Q-Bot B", (size - 1, size - 1))

    shared_q_table = {}

    for agent in (agent1, agent2):
        agent.alpha = alpha
        agent.gamma = gamma
        agent.epsilon = 0.9
        agent.q_table = shared_q_table
        agent.configure_runtime(
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

    agent1.upload()

    return {
        "alpha": alpha,
        "gamma": gamma,
        "board_size": size,
        "train_games": games,
        "shared_qtable": str(qtable_path),
    }


def main() -> None:
    """Run the full training workflow for point 2.4."""
    best_result, all_results = sweep_parameters()

    print("\nBest parameters found:")
    print(
        f"alpha={best_result['alpha']:.2f}, "
        f"gamma={best_result['gamma']:.2f}, "
        f"win_rate={best_result['win_rate']:.3f}"
    )

    self_play_result = train_self_play(
        best_result["alpha"],
        best_result["gamma"],
        LARGE_BOARD_SIZE,
        SELF_PLAY_GAMES,
    )

    summary = {
        "search": {
            "alphas": ALPHAS,
            "gammas": GAMMAS,
            "train_games": TRAIN_GAMES,
            "eval_games": EVAL_GAMES,
            "board_size": SMALL_BOARD_SIZE,
            "results": all_results,
            "best": best_result,
        },
        "self_play": self_play_result,
    }

    summary_path = RESULTS_DIR / "training_summary.json"
    summary_path.write_text(json.dumps(summary, indent=4), encoding="utf-8")

    print(f"\nSummary saved to: {summary_path}")


if __name__ == "__main__":
    main()
