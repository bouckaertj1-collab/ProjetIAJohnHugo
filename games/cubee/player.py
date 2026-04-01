import random
from typing import TYPE_CHECKING

from games.cubee.qtable_dao import build_state_key, load_qtable, save_qtable

if TYPE_CHECKING:
    from games.cubee.game_model import GameModel

QTABLE_FILE = "games/cubee/cubee_qtable.json"


class Player:
    """Base class for a Cubee player."""

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        self.name = name
        self.position = position
        self.game_model: "GameModel | None" = None

        self.nb_win: int = 0
        self.nb_lose: int = 0
        self.nb_draw: int = 0
        self.nb_game: int = 0

    def set_game_model(self, game_model: "GameModel") -> None:
        """Attach the player to a game model."""
        self.game_model = game_model

    def on_game_over(self) -> None:
        """Hook called by the model when the game ends."""

    def win(self) -> None:
        self.nb_win += 1
        self.nb_game += 1

    def lose(self) -> None:
        self.nb_lose += 1
        self.nb_game += 1

    def draw(self) -> None:
        self.nb_draw += 1
        self.nb_game += 1


class RandomAgent(Player):
    """Very simple AI that plays a random move."""

    def play(self) -> bool:
        """Choose and apply a random legal move."""
        if not self.game_model:
            return False

        moves = self.game_model.available_moves_for(self)
        if not moves:
            return False

        return self.game_model.step(random.choice(moves))


class QLearningAgent(Player):
    """AI player for Cubee using a Q-learning strategy."""

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        super().__init__(name, position)

        self.epsilon: float = 0.9
        self.alpha: float = 0.2
        self.gamma: float = 0.9

        self.previous_state: str | None = None
        self.previous_action: str | None = None

        self.q_table: dict[str, dict[str, float]] = {}

    def ensure_state_exists(self, state: str, legal_moves: list[str]) -> None:
        if state not in self.q_table:
            self.q_table[state] = {}

        for move in legal_moves:
            self.q_table[state].setdefault(move, 0.0)

    def exploit(self, state: str, legal_moves: list[str]) -> str:
        best_value = max(self.q_table[state][move] for move in legal_moves)
        best_moves = [move for move in legal_moves if self.q_table[state][move] == best_value]
        return random.choice(best_moves)

    def choose_action(self, state: str, legal_moves: list[str]) -> str:
        if random.random() < self.epsilon:
            return random.choice(legal_moves)
        return self.exploit(state, legal_moves)

    def get_current_scores(self) -> tuple[int, int]:
        """Return the current score from the agent point of view."""
        if not self.game_model:
            return 0, 0

        score_p1, score_p2 = self.game_model.score
        if self.game_model.player1 == self:
            return score_p1, score_p2
        return score_p2, score_p1

    def get_scores_from_state(self, state: str) -> tuple[int, int]:
        """Rebuild the score of a past state from its serialized board."""
        board = state.split("|")[-1]
        count_1 = board.count("1")
        count_2 = board.count("2")

        if self.game_model and self.game_model.player1 == self:
            return count_1, count_2
        return count_2, count_1

    def compute_reward(
        self,
        old_score: tuple[int, int],
        new_score: tuple[int, int],
    ) -> float:
        """Compute the reward from the agent point of view."""
        my_gain = new_score[0] - old_score[0]
        opponent_gain = new_score[1] - old_score[1]
        reward = my_gain - 1.5 * opponent_gain

        if self.game_model and self.game_model.is_game_over:
            if self.game_model.winner == self:
                reward += 10
            elif self.game_model.loser == self:
                reward -= 10

        return reward

    def learn(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str | None,
    ) -> None:
        """Apply the Q-learning update."""
        current_q = self.q_table[state][action]

        if not self.game_model or next_state is None:
            max_next_q = 0.0
        else:
            legal_moves = self.game_model.available_moves_for(self)
            if not legal_moves:
                max_next_q = 0.0
            else:
                self.ensure_state_exists(next_state, legal_moves)
                max_next_q = max(self.q_table[next_state][move] for move in legal_moves)

        target = reward + self.gamma * max_next_q
        self.q_table[state][action] = current_q + self.alpha * (target - current_q)

    def play(self) -> bool:
        """Play one move and learn from the previous full transition."""
        if not self.game_model:
            return False

        # 1. If the agent gets the hand back, finish learning
        #    from the previous move + opponent response.
        if self.previous_state is not None and self.previous_action is not None:
            old_score = self.get_scores_from_state(self.previous_state)
            new_score = self.get_current_scores()
            reward = self.compute_reward(old_score, new_score)

            next_state = build_state_key(self.game_model, self)
            legal_moves = self.game_model.available_moves_for(self)
            self.ensure_state_exists(next_state, legal_moves)

            self.learn(self.previous_state, self.previous_action, reward, next_state)

            self.previous_state = None
            self.previous_action = None

        # 2. Choose the next action
        state = build_state_key(self.game_model, self)
        legal_moves = self.game_model.available_moves_for(self)
        if not legal_moves:
            return False

        self.ensure_state_exists(state, legal_moves)
        action = self.choose_action(state, legal_moves)

        # 3. Keep this transition in memory until the agent gets the hand back
        self.previous_state = state
        self.previous_action = action

        # 4. Play
        success = self.game_model.step(action)
        if not success:
            self.previous_state = None
            self.previous_action = None
            return False

        return True

    def on_game_over(self) -> None:
        """Finalize the last pending transition if the game ends before the agent plays again."""
        if (
            self.game_model
            and self.previous_state is not None
            and self.previous_action is not None
        ):
            old_score = self.get_scores_from_state(self.previous_state)
            new_score = self.get_current_scores()
            reward = self.compute_reward(old_score, new_score)

            self.learn(self.previous_state, self.previous_action, reward, None)

            self.previous_state = None
            self.previous_action = None

        self.upload()
        self.next_epsilon()

    def next_epsilon(self, coef: float = 0.995, min_epsilon: float = 0.05) -> None:
        self.epsilon = max(min_epsilon, self.epsilon * coef)

    def upload(self, filename: str = QTABLE_FILE) -> None:
        save_qtable(filename, self.q_table, self.epsilon, self.alpha, self.gamma)

    def download(self, filename: str = QTABLE_FILE) -> None:
        data = load_qtable(filename)
        self.epsilon = data["epsilon"]
        self.alpha = data["alpha"]
        self.gamma = data["gamma"]
        self.q_table = data["q_table"]