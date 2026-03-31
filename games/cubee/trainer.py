from pathlib import Path

from games.cubee.game_model import GameModel
from games.cubee.player import QLearningAgent, RandomAgent


PARAM_GRID = [
    (0.10, 0.20),
    (0.10, 0.40),
    (0.10, 0.60),
    (0.10, 0.80),
    (0.15, 0.20),
    (0.15, 0.40),
    (0.15, 0.60),
    (0.15, 0.80),
    (0.20, 0.20),
    (0.20, 0.40),
    (0.20, 0.60),
    (0.20, 0.70),
    (0.20, 0.72),
    (0.20, 0.74),
    (0.20, 0.80),
    (0.20, 0.82),
    (0.20, 0.84),
    (0.20, 0.86)
]


class CubeeTrainer:
    def __init__(self, size: int = 3, save_dir: str = "games/cubee/training_results") -> None:
        self.size = size
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def _update_agent_before_move(self, agent: QLearningAgent, model: GameModel) -> None:
        if agent.previous_score is None:
            return

        reward = agent.compute_reward(agent.previous_score, model.score, model)
        agent.learn(reward, model)
        agent.previous_score = None

    def _finalize_agent(self, agent: QLearningAgent, model: GameModel) -> None:
        if agent.previous_score is not None:
            reward = agent.compute_reward(agent.previous_score, model.score, model)
            agent.learn(reward, None)

        agent.reset_memory()

    def _play_episode(self, model: GameModel, learning: bool = True) -> None:
        if isinstance(model.player1, QLearningAgent):
            model.player1.reset_memory()
        if isinstance(model.player2, QLearningAgent):
            model.player2.reset_memory()

        while not model.is_game_over:
            current = model.current_player

            if isinstance(current, QLearningAgent):
                if learning:
                    self._update_agent_before_move(current, model)

                old_score = model.score
                move = current.play(model)

                if not model.step(move):
                    raise RuntimeError(f"Illegal move played by QLearningAgent: {move}")

                if learning:
                    current.previous_score = old_score

            elif isinstance(current, RandomAgent):
                move = current.play(model)

                if not model.step(move):
                    raise RuntimeError(f"Illegal move played by RandomAgent: {move}")

            else:
                raise TypeError("Trainer only supports QLearningAgent and RandomAgent.")

        if isinstance(model.player1, QLearningAgent):
            self._finalize_agent(model.player1, model)
        if isinstance(model.player2, QLearningAgent):
            self._finalize_agent(model.player2, model)

    def _build_filename(self, alpha: float, gamma: float) -> str:
        return str(self.save_dir / f"qtable_alpha_{alpha:.2f}_gamma_{gamma:.2f}.json")

    def train_vs_random(
        self,
        alpha: float,
        gamma: float,
        episodes: int = 3000,
        epsilon_start: float = 0.9,
        epsilon_decay: float = 0.999,
        epsilon_min: float = 0.05,
        save_qtable: bool = True,
    ) -> QLearningAgent:
        q_agent = QLearningAgent("Q-Bot", (0, 0))
        q_agent.alpha = alpha
        q_agent.gamma = gamma
        q_agent.epsilon = epsilon_start

        random_agent = RandomAgent("Random", (self.size - 1, self.size - 1))
        model = GameModel(q_agent, random_agent, size=self.size)

        for _ in range(episodes):
            model.reset()
            self._play_episode(model, learning=True)
            q_agent.next_epsilon(epsilon_decay, epsilon_min)

        if save_qtable:
            q_agent.upload(self._build_filename(alpha, gamma))

        return q_agent

    def evaluate_vs_random(self, trained_agent: QLearningAgent, games: int = 500) -> dict:
        eval_agent = QLearningAgent("Q-Eval", (0, 0))
        eval_agent.alpha = trained_agent.alpha
        eval_agent.gamma = trained_agent.gamma
        eval_agent.epsilon = 0.0
        eval_agent.q_table = trained_agent.q_table

        random_agent = RandomAgent("Random", (self.size - 1, self.size - 1))
        model = GameModel(eval_agent, random_agent, size=self.size)

        for _ in range(games):
            model.reset()
            self._play_episode(model, learning=False)

        return {
            "wins": eval_agent.nb_win,
            "losses": eval_agent.nb_lose,
            "draws": eval_agent.nb_draw,
            "win_rate": eval_agent.nb_win / games,
            "loss_rate": eval_agent.nb_lose / games,
            "draw_rate": eval_agent.nb_draw / games,
        }

    def benchmark_parameters(
        self,
        param_grid: list[tuple[float, float]] = PARAM_GRID,
        train_episodes: int = 3000,
        eval_games: int = 500,
        save_qtables: bool = True,
    ) -> list[dict]:
        results = []

        for alpha, gamma in param_grid:
            agent = self.train_vs_random(
                alpha=alpha,
                gamma=gamma,
                episodes=train_episodes,
                save_qtable=save_qtables,
            )

            stats = self.evaluate_vs_random(agent, games=eval_games)

            results.append(
                {
                    "alpha": alpha,
                    "gamma": gamma,
                    "epsilon_final": agent.epsilon,
                    "qtable_size": len(agent.q_table),
                    **stats,
                }
            )

        results.sort(key=lambda row: row["win_rate"], reverse=True)
        return results