import random
from games.cubee.qtable_dao import QTableDAO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.cubee.game_model import GameModel

QTABLE_FILE = "games/cubee/cubee_qtable.json"


class Player:
    """Base class for a Cubee player."""

    def __init__(self, name: str, position: tuple[int, int],) -> None:
        """
        Initialize a player.

        Args:
            name: The player name.
            position: The current player position on the board.
        """
        self.name = name
        self.position = position

        self.nb_win: int = 0
        self.nb_lose: int = 0
        self.nb_draw: int = 0
        self.nb_game: int = 0

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
    """Very simple AI that plays a random move."""

    def play(self, game_model) -> str:
        """
        Choose and return a random legal move.

        Args:
            game_model: The current game model.

        Returns:
            A random legal move.
        """
        moves = game_model.available_moves()
        return random.choice(moves)
    

class QLearningAgent(Player):
    """AI player for Cubee using a Q-learning strategy."""

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        """
        Initialize a Q-learning agent.

        Args:
            name: Player name.
            position: Initial position of the player on the board.
        """
        super().__init__(name, position)

        self.epsilon: float = 0.9
        self.alpha: float = 0.2
        self.gamma: float = 0.9
        self.previous_score: tuple[int, int] | None = None
        self.previous_state: str | None = None
        self.previous_action: str | None = None

        self.q_table: dict[str, dict[str, float]] = {}

    def get_state_key(self, game_model) -> str:
        """
        Build a compact representation of the current state for the Q-table.

        The state is described from the AI point of view using:
        - the current turn
        - the AI position
        - the opponent position
        - the serialized board

        Args:
            game_model: Current Cubee game model.

        Returns:
            A string uniquely describing the current state.
        """
        if game_model.player1 == self:
            my_pos = game_model.player1.position
            opp_pos = game_model.player2.position
        else:
            my_pos = game_model.player2.position
            opp_pos = game_model.player1.position

        my_row, my_col = my_pos
        opp_row, opp_col = opp_pos
        turn = game_model.player_turn
        board = game_model.board_to_string()

        return f"{turn}|{my_row},{my_col}|{opp_row},{opp_col}|{board}"

    def ensure_state_exists(self, state: str, legal_moves: list[str]) -> None:
        """
        Ensure that a state and its legal actions exist in the Q-table.

        If the state does not exist yet, it is created.
        If an action is missing for this state, it is initialized to 0.0.

        Args:
            state: Serialized state key.
            legal_moves: Legal actions available in this state.
        """
        if state not in self.q_table:
            self.q_table[state] = {}

        for move in legal_moves:
            if move not in self.q_table[state]:
                self.q_table[state][move] = 0.0

    def play(self, game_model) -> str:
        """
        Choose an action using an epsilon-greedy strategy.

        With probability epsilon, the agent explores by choosing a random move.
        Otherwise, it exploits the best known move.

        Args:
            game_model: Current Cubee game model.

        Returns:
            The selected action.
        """
        state = self.get_state_key(game_model)
        legal_moves = game_model.available_moves()

        self.ensure_state_exists(state, legal_moves)
        self.previous_state = state

        action = (random.choice(legal_moves) if random.random() < self.epsilon else self.exploit(state, legal_moves))

        self.previous_action = action
        return action

    def exploit(self, state: str, legal_moves: list[str]) -> str:
        """
        Choose the best known action for a given state.

        If several actions have the same best value, one of them is chosen
        randomly.

        Args:
            state: Serialized state key.
            legal_moves: Legal actions available in this state.

        Returns:
            The selected action.
        """
        best_value = max(self.q_table[state][move] for move in legal_moves)
        best_moves = [move for move in legal_moves if self.q_table[state][move] == best_value]
        return random.choice(best_moves)
    
    def learn(self, reward: float, game_model: "GameModel | None") -> None:
        """
        Update the Q-table after the previous action.

        Args:
            reward: Reward obtained for the last transition.
            game_model: Current game state, or None if the game is over.
        """
        if self.previous_state is None:
            return

        if game_model is None:
            max_next_q = 0.0
        else:
            new_state = self.get_state_key(game_model)
            legal_moves = game_model.available_moves()
            self.ensure_state_exists(new_state, legal_moves)
            max_next_q = max(self.q_table[new_state][move] for move in legal_moves)

        current_q = self.q_table[self.previous_state][self.previous_action]
        target = reward + self.gamma * max_next_q
        self.q_table[self.previous_state][self.previous_action] = (
            current_q + self.alpha * (target - current_q)
        )

    def compute_reward(self, old_score: tuple[int, int], new_score: tuple[int, int], game_model) -> float:
        """
        Compute the reward from the AI point of view.

        The reward is based on the score evolution over a full transition
        between two decision states of the AI:
        - gaining territory increases the reward
        - allowing the opponent to gain territory decreases the reward more strongly
        - a bonus is added for a victory
        - a penalty is added for a defeat

        Args:
            old_score: Score at the beginning of the transition.
            new_score: Score at the end of the transition.
            game_model: Current Cubee game model.

        Returns:
            The reward associated with the transition.
        """
        if game_model.player1 == self:
            my_old, opp_old = old_score[0], old_score[1]
            my_new, opp_new = new_score[0], new_score[1]
        else:
            my_old, opp_old = old_score[1], old_score[0]
            my_new, opp_new = new_score[1], new_score[0]

        my_gain = my_new - my_old
        opp_gain = opp_new - opp_old

        reward = my_gain - 1.5 * opp_gain

        if game_model.is_game_over:
            if game_model.winner == self:
                reward += 10
            elif game_model.winner is not None:
                reward -= 10

        return reward

    def next_epsilon(self, coef: float = 0.995, min_epsilon: float = 0.05) -> None:
        """
        Reduce exploration progressively after each game.

        Args:
            coef: Multiplicative decay coefficient.
            min_epsilon: Minimum exploration rate allowed.
        """
        self.epsilon = max(min_epsilon, self.epsilon * coef)

    def reset_memory(self) -> None:
        """
        Reset the temporary memory used between actions.

        This is useful between two games to avoid reusing information
        from the previous match.
        """
        self.previous_state = None
        self.previous_action = None
        self.previous_score = None

    def upload(self, filename: str = QTABLE_FILE) -> None:
        """
        Save the Q-table and learning parameters to a file.

        Args:
            filename: Path of the JSON file used for persistence.
        """
        QTableDAO.save(
            filename,
            self.q_table,
            self.epsilon,
            self.alpha,
            self.gamma,
        )

    def download(self, filename: str = QTABLE_FILE) -> None:
        """
        Load the Q-table and learning parameters from a file.

        Args:
            filename: Path of the JSON file used for persistence.
        """
        data = QTableDAO.load(filename)
        self.epsilon = data["epsilon"]
        self.alpha = data["alpha"]
        self.gamma = data["gamma"]
        self.q_table = data["q_table"]