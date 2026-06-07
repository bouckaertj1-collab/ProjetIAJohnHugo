import copy
import csv
import random
import statistics
from pathlib import Path

from games.cubee.game_model import GameModel
from games.cubee.player import QLearningAgent
from games.cubee.qtable_dao import build_state_key


ALPHAS = [0.05, 0.10, 0.20, 0.40]
GAMMAS = [0.20, 0.40, 0.60, 0.80]

BOARD_SIZE = 4
TRAINING_CHECKPOINTS = [10_000, 25_000, 50_000, 100_000, 200_000]
TUNING_EVAL_GAMES = 2_000
SEEDS = [1, 2, 3]

EPSILON_DECAY_COEF = 0.999985
MIN_EPSILON = 0.05

RESULTS_DIR = Path(__file__).resolve().parent / "training_results"
REFERENCE_QTABLE_PATH = Path(__file__).resolve().parent / "cubee_reference_4x4_qtable.json"

CHECKPOINTS_CSV_PATH = RESULTS_DIR / "parameter_tuning_checkpoints.csv"
SUMMARY_CSV_PATH = RESULTS_DIR / "parameter_tuning_summary.csv"
SUMMARY_MD_PATH = RESULTS_DIR / "parameter_tuning_summary.md"


class FrozenQLearningAgent(QLearningAgent):
    """
    Q-learning agent used only as a fixed player.

    It uses an existing Q-table to choose actions, but it does not learn,
    does not save, does not decrease epsilon, and does not add new states
    to the Q-table during evaluation.
    """

    def play(self) -> bool:
        """
        Play one greedy move without modifying the Q-table.

        If the current state is unknown, the agent uses 0.0 as the default
        value for missing actions and chooses randomly among tied best moves.
        """
        if self.game_model is None:
            return False

        legal_moves = self.game_model.available_moves_for(self)
        state_key = build_state_key(self.game_model, self)
        action_values = self.q_table.get(state_key, {})

        best_value = max(action_values.get(move, 0.0) for move in legal_moves)
        best_moves = [
            move
            for move in legal_moves
            if action_values.get(move, 0.0) == best_value
        ]

        return self.game_model.step(random.choice(best_moves))


def play_full_game(model: GameModel) -> None:
    """
    Play a complete game without graphical interface.
    """
    while not model.is_game_over:
        model.current_player.play()


def create_fixed_opponent() -> FrozenQLearningAgent:
    """
    Create the fixed 4x4 reference opponent.

    This opponent is loaded from the reference Q-table and never modifies it.
    """
    opponent = FrozenQLearningAgent("Fixed-Q-Bot", (BOARD_SIZE - 1, BOARD_SIZE - 1))

    opponent.configure_learning(
        learning_enabled=False,
        auto_save=False,
        auto_decay=False,
        qtable_filename=str(REFERENCE_QTABLE_PATH),
    )

    opponent.load(str(REFERENCE_QTABLE_PATH))
    opponent.epsilon = 0.0

    return opponent


def create_candidate(alpha: float, gamma: float) -> QLearningAgent:
    """
    Create a Q-learning candidate with the tested alpha/gamma values.
    """
    candidate = QLearningAgent("Candidate", (0, 0))
    candidate.alpha = alpha
    candidate.gamma = gamma
    candidate.epsilon = 0.9

    candidate.configure_learning(
        learning_enabled=True,
        auto_save=False,
        auto_decay=True,
    )

    return candidate


def create_frozen_candidate(candidate: QLearningAgent) -> FrozenQLearningAgent:
    """
    Create a frozen copy of a trained candidate for evaluation.
    """
    frozen_candidate = FrozenQLearningAgent("Candidate", (0, 0))
    frozen_candidate.q_table = copy.deepcopy(candidate.q_table)
    frozen_candidate.alpha = candidate.alpha
    frozen_candidate.gamma = candidate.gamma
    frozen_candidate.epsilon = 0.0

    frozen_candidate.configure_learning(
        learning_enabled=False,
        auto_save=False,
        auto_decay=False,
    )

    return frozen_candidate


def evaluate_candidate(candidate: QLearningAgent, seed: int) -> dict:
    """
    Evaluate a trained candidate against the fixed opponent.

    Both agents are frozen during evaluation, so no Q-table is modified.
    """
    random.seed(seed)

    evaluator = create_frozen_candidate(candidate)
    fixed_opponent = create_fixed_opponent()

    model = GameModel(evaluator, fixed_opponent, size=BOARD_SIZE)

    wins = 0
    losses = 0
    draws = 0
    score_margins = []

    for game_index in range(TUNING_EVAL_GAMES):
        play_full_game(model)

        candidate_score, opponent_score = model.score
        score_margins.append(candidate_score - opponent_score)

        if model.winner is evaluator:
            wins += 1
        elif model.winner is fixed_opponent:
            losses += 1
        else:
            draws += 1

        if game_index < TUNING_EVAL_GAMES - 1:
            model.reset()

    return {
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": wins / TUNING_EVAL_GAMES,
        "loss_rate": losses / TUNING_EVAL_GAMES,
        "draw_rate": draws / TUNING_EVAL_GAMES,
        "average_score_margin": sum(score_margins) / TUNING_EVAL_GAMES,
    }


def train_and_evaluate_checkpoints(alpha: float, gamma: float, seed: int) -> list[dict]:
    """
    Train one candidate and evaluate it at several checkpoints.

    This measures both final performance and learning speed. It is more useful
    for comparing alpha values than evaluating only after full convergence.
    """
    random.seed(seed)

    candidate = create_candidate(alpha, gamma)
    fixed_opponent = create_fixed_opponent()
    model = GameModel(candidate, fixed_opponent, size=BOARD_SIZE)

    rows = []
    max_games = max(TRAINING_CHECKPOINTS)

    for game_index in range(1, max_games + 1):
        play_full_game(model)

        if game_index in TRAINING_CHECKPOINTS:
            training_random_state = random.getstate()

            evaluation_seed = seed + 10_000 + game_index
            evaluation = evaluate_candidate(candidate, evaluation_seed)

            qtable_states = len(candidate.q_table)
            qtable_actions = sum(len(actions) for actions in candidate.q_table.values())

            rows.append({
                "alpha": alpha,
                "gamma": gamma,
                "epsilon_decay_coef": EPSILON_DECAY_COEF,
                "min_epsilon": MIN_EPSILON,
                "seed": seed,
                "board_size": BOARD_SIZE,
                "checkpoint_games": game_index,
                "eval_games": TUNING_EVAL_GAMES,
                "wins": evaluation["wins"],
                "losses": evaluation["losses"],
                "draws": evaluation["draws"],
                "win_rate": evaluation["win_rate"],
                "loss_rate": evaluation["loss_rate"],
                "draw_rate": evaluation["draw_rate"],
                "average_score_margin": evaluation["average_score_margin"],
                "qtable_states": qtable_states,
                "qtable_actions": qtable_actions,
            })

            random.setstate(training_random_state)

            print(
                f"Checkpoint alpha={alpha}, gamma={gamma}, seed={seed}, "
                f"games={game_index}, win_rate={evaluation['win_rate']:.4f}, "
                f"margin={evaluation['average_score_margin']:.4f}"
            )

        if game_index < max_games:
            model.reset()

    return rows


def save_csv(path: Path, rows: list[dict]) -> None:
    """
    Save a list of dictionaries as a CSV file.
    """
    if not rows:
        return

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def aggregate_results(checkpoint_rows: list[dict]) -> list[dict]:
    """
    Aggregate checkpoint results by alpha/gamma pair.

    learning_score is the average win rate over all checkpoints and seeds.
    final_win_rate is the average win rate at the last checkpoint only.
    """
    summary_results = []
    final_checkpoint = max(TRAINING_CHECKPOINTS)

    for alpha in ALPHAS:
        for gamma in GAMMAS:
            matching_rows = [
                row for row in checkpoint_rows
                if row["alpha"] == alpha and row["gamma"] == gamma
            ]

            final_rows = [
                row for row in matching_rows
                if row["checkpoint_games"] == final_checkpoint
            ]

            learning_win_rates = [row["win_rate"] for row in matching_rows]
            learning_margins = [row["average_score_margin"] for row in matching_rows]

            final_win_rates = [row["win_rate"] for row in final_rows]
            final_loss_rates = [row["loss_rate"] for row in final_rows]
            final_draw_rates = [row["draw_rate"] for row in final_rows]
            final_margins = [row["average_score_margin"] for row in final_rows]
            final_states = [row["qtable_states"] for row in final_rows]
            final_actions = [row["qtable_actions"] for row in final_rows]

            summary_results.append({
                "alpha": alpha,
                "gamma": gamma,
                "epsilon_decay_coef": EPSILON_DECAY_COEF,
                "min_epsilon": MIN_EPSILON,
                "board_size": BOARD_SIZE,
                "seeds": len(SEEDS),
                "checkpoints": str(TRAINING_CHECKPOINTS),
                "eval_games_per_checkpoint": TUNING_EVAL_GAMES,
                "learning_score": statistics.mean(learning_win_rates),
                "learning_score_margin": statistics.mean(learning_margins),
                "final_win_rate": statistics.mean(final_win_rates),
                "final_loss_rate": statistics.mean(final_loss_rates),
                "final_draw_rate": statistics.mean(final_draw_rates),
                "final_score_margin": statistics.mean(final_margins),
                "final_win_rate_std": statistics.stdev(final_win_rates) if len(final_win_rates) > 1 else 0.0,
                "average_final_qtable_states": round(statistics.mean(final_states), 2),
                "average_final_qtable_actions": round(statistics.mean(final_actions), 2),
            })

    return sorted(
        summary_results,
        key=lambda result: (
            result["learning_score"],
            result["final_win_rate"],
            result["final_score_margin"],
        ),
        reverse=True,
    )


def save_markdown_summary(summary_results: list[dict]) -> None:
    """
    Save a readable Markdown summary of the parameter tuning results.
    """
    best_result = summary_results[0]

    lines = [
        "# Cubee parameter tuning summary",
        "",
        "## Method",
        "",
        f"- Board size: `{BOARD_SIZE}`",
        f"- Training checkpoints: `{TRAINING_CHECKPOINTS}`",
        f"- Evaluation games per checkpoint: `{TUNING_EVAL_GAMES}`",
        f"- Seeds: `{SEEDS}`",
        f"- Epsilon decay coefficient: `{EPSILON_DECAY_COEF}`",
        f"- Minimum epsilon: `{MIN_EPSILON}`",
        f"- Reference Q-table: `{REFERENCE_QTABLE_PATH}`",
        "",
        "Each alpha/gamma pair is trained once per seed and evaluated at several checkpoints.",
        "The main metric is the learning score, which averages win rate over all checkpoints.",
        "This makes alpha easier to compare because alpha mainly affects learning speed.",
        "",
        "## Best result",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Alpha | {best_result['alpha']} |",
        f"| Gamma | {best_result['gamma']} |",
        f"| Learning score | {best_result['learning_score']:.4f} |",
        f"| Learning score margin | {best_result['learning_score_margin']:.4f} |",
        f"| Final win rate | {best_result['final_win_rate']:.4f} |",
        f"| Final loss rate | {best_result['final_loss_rate']:.4f} |",
        f"| Final draw rate | {best_result['final_draw_rate']:.4f} |",
        f"| Final score margin | {best_result['final_score_margin']:.4f} |",
        "",
        "## All parameter combinations",
        "",
        "| Rank | Alpha | Gamma | Learning score | Final win | Final loss | Final draw | Final margin | Final std |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for rank, result in enumerate(summary_results, start=1):
        lines.append(
            f"| {rank} "
            f"| {result['alpha']} "
            f"| {result['gamma']} "
            f"| {result['learning_score']:.4f} "
            f"| {result['final_win_rate']:.4f} "
            f"| {result['final_loss_rate']:.4f} "
            f"| {result['final_draw_rate']:.4f} "
            f"| {result['final_score_margin']:.4f} "
            f"| {result['final_win_rate_std']:.4f} |"
        )

    lines.append("")
    SUMMARY_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def tune_parameters() -> None:
    """
    Run the alpha/gamma parameter tuning process.

    Checkpoint results are saved after every completed alpha/gamma/seed run.
    """
    if not REFERENCE_QTABLE_PATH.exists():
        raise FileNotFoundError(
            f"Reference Q-table not found: {REFERENCE_QTABLE_PATH}\n"
            "Train the 4x4 reference Q-table first."
        )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    checkpoint_rows = []
    total_runs = len(ALPHAS) * len(GAMMAS) * len(SEEDS)
    completed_runs = 0

    for alpha in ALPHAS:
        for gamma in GAMMAS:
            for seed in SEEDS:
                print(f"\nTesting alpha={alpha:.2f}, gamma={gamma:.2f}, seed={seed}")

                rows = train_and_evaluate_checkpoints(alpha, gamma, seed)
                checkpoint_rows.extend(rows)

                completed_runs += 1
                save_csv(CHECKPOINTS_CSV_PATH, checkpoint_rows)

                print(f"Saved checkpoint results: {completed_runs}/{total_runs} runs completed")

    summary_results = aggregate_results(checkpoint_rows)

    save_csv(SUMMARY_CSV_PATH, summary_results)
    save_markdown_summary(summary_results)

    best_result = summary_results[0]

    print("\nParameter tuning completed.")
    print(f"Best alpha: {best_result['alpha']}")
    print(f"Best gamma: {best_result['gamma']}")
    print(f"Learning score: {best_result['learning_score']:.4f}")
    print(f"Final win rate: {best_result['final_win_rate']:.4f}")
    print(f"Checkpoint CSV saved to: {CHECKPOINTS_CSV_PATH}")
    print(f"Summary CSV saved to: {SUMMARY_CSV_PATH}")
    print(f"Markdown summary saved to: {SUMMARY_MD_PATH}")


if __name__ == "__main__":
    tune_parameters()