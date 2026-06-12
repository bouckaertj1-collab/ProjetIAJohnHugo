import random
from pathlib import Path
from typing import TYPE_CHECKING

from games.cubee.qtable_dao import build_state_key, load_qtable, save_qtable

if TYPE_CHECKING:
    from games.cubee.game_model import GameModel

QTABLE_FILE = "games/cubee/cubee_qtable.json"


class Player:
    """Base class for a Cubee player."""

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        """
        Initialize a player.

        Args:
            name: Player name.
            position: Current position on the board.
        """
        self.name = name
        self.position = position
        self.game_model: "GameModel | None" = None

        self.nb_win: int = 0
        self.nb_lose: int = 0
        self.nb_draw: int = 0
        self.nb_game: int = 0

    def finalize_learning(self) -> None:
        """
        Method called by the model when the game ends.

        The default implementation does nothing. AI players can override
        this method to finalize learning or save their state.
        """
        pass

    def win(self) -> None:
        """Record a win for this player."""
        self.nb_win += 1
        self.nb_game += 1

    def lose(self) -> None:
        """Record a loss for this player."""
        self.nb_lose += 1
        self.nb_game += 1

    def draw(self) -> None:
        """Record a draw for this player."""
        self.nb_draw += 1
        self.nb_game += 1


class RandomAgent(Player):
    """Simple AI that plays a random legal move."""

    def play(self) -> bool:
        """
        Choose and apply a random legal move.

        Returns:
            True if a move was played, False otherwise.
        """
        if not self.game_model:
            return False

        moves = self.game_model.available_moves_for(self)

        return self.game_model.step(random.choice(moves))


class QLearningAgent(Player):
    """AI player for Cubee using a Q-learning strategy."""

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        """
        Initialize a Q-learning agent.

        Args:
            name: Player name.
            position: Initial position on the board.
        """
        super().__init__(name, position)

        self.epsilon: float = 0.9
        self.alpha: float = 0.2
        self.gamma: float = 0.9

        self.previous_state: str | None = None
        self.previous_action: str | None = None
        self.previous_score: tuple[int, int] | None = None

        self.q_table: dict[str, dict[str, float]] = {}

        self.learning_enabled: bool = True
        self.auto_save: bool = True
        self.auto_decay: bool = True
        self.qtable_filename: str = QTABLE_FILE

    def configure_learning(
        self,
        *,
        learning_enabled: bool | None = None,
        auto_save: bool | None = None,
        auto_decay: bool | None = None,
        qtable_filename: str | None = None,
    ) -> None:
        """Configure how the agent behaves during training or evaluation."""
        if learning_enabled is not None:
            self.learning_enabled = learning_enabled
        if auto_save is not None:
            self.auto_save = auto_save
        if auto_decay is not None:
            self.auto_decay = auto_decay
        if qtable_filename is not None:
            self.qtable_filename = qtable_filename

    def play(self) -> None:
        """
        Play one move and learn from the previous full transition.

        If learning is enabled and a previous transition is stored, the agent
        first updates its in-memory Q-table from the previously stored state,
        action and score. It then chooses a new action, stores the current
        transition, and applies the move to the model.
        """
        if self.previous_state and self.previous_action and self.previous_score:
            if self.learning_enabled:
                new_score = self.get_scores_from_agent_view()
                reward = self.compute_reward(self.previous_score, new_score)

                next_state = build_state_key(self.game_model, self)
                legal_moves = self.game_model.available_moves_for(self)
                self.ensure_state_exists(next_state, legal_moves)

                self.learn(self.previous_state, self.previous_action, reward, next_state)

            self.reset_memory()

        state = build_state_key(self.game_model, self)
        legal_moves = self.game_model.available_moves_for(self)

        self.ensure_state_exists(state, legal_moves)
        action = self.choose_action(state, legal_moves)

        self.previous_state = state
        self.previous_action = action
        self.previous_score = self.get_scores_from_agent_view()

        self.game_model.step(action)
    
    def exploit(self, state: str, legal_moves: list[str]) -> str:
        """
        Choose the best known action for a given state.

        If several actions share the same best value, one of them is
        selected randomly.

        Args:
            state: Serialized state key.
            legal_moves: Legal actions available in this state.

        Returns:
            One of the best actions for this state.
        """
        best_value = max(self.q_table[state][move] for move in legal_moves)
        best_moves = [move for move in legal_moves if self.q_table[state][move] == best_value]
        return random.choice(best_moves)
    
    def compute_reward(self, old_score: tuple[int, int], new_score: tuple[int, int]) -> float:
        """
        Compute the reward from the agent point of view.

        The reward compares the score before the agent move and the score
        observed when the agent gets the hand back. A terminal bonus or
        penalty is added if the game is over.

        Args:
            old_score: Score before the agent move.
            new_score: Score when the agent evaluates the full transition.

        Returns:
            The reward associated with the previous action.
        """
        my_gain = new_score[0] - old_score[0]
        opponent_gain = new_score[1] - old_score[1]
        reward = my_gain - 1.5 * opponent_gain

        if self.game_model.is_game_over:
            if self.game_model.winner == self:
                reward += 10
            elif self.game_model.loser == self:
                reward -= 10

        return reward

    def learn(
        self,
        previous_state: str,
        previous_action: str,
        reward: float,
        next_state: str | None
    ) -> None:
        """
        Update the Q-table for the previous state-action pair.

        Args:
            previous_state: State where the agent chose the previous action.
            previous_action: Action chosen from the previous state.
            reward: Reward obtained after this action.
            next_state: State reached after the action, or None if the game is over.
        """
        old_q = self.q_table[previous_state][previous_action]

        if next_state is None:
            best_future_q = 0.0
        else:
            legal_moves = self.game_model.available_moves_for(self)
            self.ensure_state_exists(next_state, legal_moves)
            best_future_q = max(
                self.q_table[next_state][move]
                for move in legal_moves
            )

        target_q = reward + self.gamma * best_future_q
        updated_old_q = old_q + self.alpha * (target_q - old_q)

        self.q_table[previous_state][previous_action] = updated_old_q

    def finalize_learning(self) -> None:
        """
        Finalize the last pending transition when the game ends.

        If the agent has a move still waiting to be evaluated, the final
        reward is computed here before saving the Q-table.
        """
        if self.learning_enabled and self.previous_state and self.previous_action and self.previous_score:
            new_score = self.get_scores_from_agent_view()
            reward = self.compute_reward(self.previous_score, new_score)
            self.learn(self.previous_state, self.previous_action, reward, None)
            self.reset_memory()

        if self.auto_save:
            self.save()
        if self.auto_decay:
            self.next_epsilon()

    def ensure_state_exists(self, state: str, legal_moves: list[str]) -> None:
        """
        Ensure that a state and its legal actions exist in the Q-table.

        Args:
            state: Serialized state key.
            legal_moves: Legal actions available in this state.
        """
        if state not in self.q_table:
            self.q_table[state] = {}

        for move in legal_moves:
            self.q_table[state].setdefault(move, 0.0)

    def choose_action(self, state: str, legal_moves: list[str]) -> str:
        """
        Choose an action with an epsilon-greedy policy.

        Args:
            state: Serialized state key.
            legal_moves: Legal actions available in this state.

        Returns:
            The selected action.
        """
        if random.random() < self.epsilon:
            return random.choice(legal_moves)
        return self.exploit(state, legal_moves)

    def get_scores_from_agent_view(self) -> tuple[int, int]:
        """
        Return the current score from the agent point of view.

        Returns:
            A tuple (my_score, opponent_score).
        """
        if not self.game_model:
            return 0, 0

        score_p1, score_p2 = self.game_model.score
        if self.game_model.player1 == self:
            return score_p1, score_p2
        return score_p2, score_p1

    def reset_memory(self) -> None:
        """Reset the pending transition."""
        self.previous_state = None
        self.previous_action = None
        self.previous_score = None

    def next_epsilon(self, coef: float = 0.99999, min_epsilon: float = 0.05) -> None:
        """
        Reduce exploration progressively after each game.

        Args:
            coef: Multiplicative decay coefficient.
            min_epsilon: Minimum exploration rate allowed.
        """
        self.epsilon = max(min_epsilon, self.epsilon * coef)

    def save(self, filename: str | None = None) -> None:
        """
        Save the Q-table and learning parameters to a file.

        Args:
            filename: Path of the JSON file used for persistence.
        """
        output = filename or self.qtable_filename
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        save_qtable(output, self.q_table, self.epsilon, self.alpha, self.gamma)

    def load(self, filename: str | None = None) -> None:
        """
        Load the Q-table and learning parameters from a file.

        Args:
            filename: Path of the JSON file used for persistence.
        """
        source = filename or self.qtable_filename
        data = load_qtable(source)
        self.epsilon = data["epsilon"]
        self.alpha = data["alpha"]
        self.gamma = data["gamma"]
        self.q_table = data["q_table"]