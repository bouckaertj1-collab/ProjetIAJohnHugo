import random
from games.cubee.qtable_dao import QTableDAO

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
    
    def is_ai(self) -> bool:
        """
        Tell whether this player is controlled by the AI.

        Returns:
            False for a regular player.
        """
        return False


class RandomAgent(Player):
    """Very simple AI that plays a random move."""

    def is_ai(self) -> bool:
        """
        Tell whether this player is controlled by the AI.

        Returns:
            True for this AI player.
        """
        return True

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
    """Cubee AI using Q-learning."""

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        super().__init__(name, position)

        self.epsilon: float = 0.9
        self.alpha: float = 0.2
        self.gamma: float = 0.9

        self.q_table: dict[str, dict[str, float]] = {}

        self.previous_state: str | None = None
        self.previous_action: str | None = None

    def is_ai(self) -> bool:
        return True

    def get_state_key(self, game_model) -> str:
        """
        Build a state string from the AI point of view.
        """
        if game_model.player1 == self:
            my_pos = game_model.player1.position
            opp_pos = game_model.player2.position
        else:
            my_pos = game_model.player2.position
            opp_pos = game_model.player1.position

        my_row, my_col = my_pos
        opp_row, opp_col = opp_pos
        board = game_model.board_to_string()

        return f"{my_row},{my_col}|{opp_row},{opp_col}|{board}"

    def ensure_state_exists(self, state: str, legal_moves: list[str]) -> None:
        """
        Create the state in the Q-table if it does not exist yet.
        """
        if state not in self.q_table:
            self.q_table[state] = {}

        for move in legal_moves:
            if move not in self.q_table[state]:
                self.q_table[state][move] = 0.0

    def exploit(self, game_model) -> str:
        """
        Choose the best move according to the Q-table.
        """
        state = self.get_state_key(game_model)
        legal_moves = game_model.available_moves()

        self.ensure_state_exists(state, legal_moves)

        best_value = max(self.q_table[state][move] for move in legal_moves)
        best_moves = [
            move for move in legal_moves
            if self.q_table[state][move] == best_value
        ]

        return random.choice(best_moves)

    def play(self, game_model) -> str:
        """
        Choose a move using epsilon-greedy.
        """
        state = self.get_state_key(game_model)
        legal_moves = game_model.available_moves()

        self.ensure_state_exists(state, legal_moves)

        self.previous_state = state

        if random.random() < self.epsilon:
            action = random.choice(legal_moves)
        else:
            action = self.exploit(game_model)

        self.previous_action = action
        return action

    def learn(self, reward: float, new_state: str, new_legal_moves: list[str], done: bool) -> None:
        """
        Update the Q-table after one move.
        """
        if self.previous_state is None or self.previous_action is None:
            return

        self.ensure_state_exists(self.previous_state, [self.previous_action])

        if not done:
            self.ensure_state_exists(new_state, new_legal_moves)
            max_next_q = max(self.q_table[new_state][move] for move in new_legal_moves)
        else:
            max_next_q = 0.0

        old_q = self.q_table[self.previous_state][self.previous_action]

        new_q = old_q + self.alpha * (
            reward + self.gamma * max_next_q - old_q
        )

        self.q_table[self.previous_state][self.previous_action] = new_q

    def compute_reward(self, old_score: tuple[int, int], new_score: tuple[int, int], game_model) -> float:
        """
        Compute the reward from the AI point of view.
        """
        if game_model.player1 == self:
            my_old, opp_old = old_score[0], old_score[1]
            my_new, opp_new = new_score[0], new_score[1]
        else:
            my_old, opp_old = old_score[1], old_score[0]
            my_new, opp_new = new_score[1], new_score[0]

        reward = (my_new - my_old) - (opp_new - opp_old)

        if game_model.is_game_over:
            if game_model.winner == self:
                reward += 10
            elif game_model.winner is not None:
                reward -= 10

        return reward

    def next_epsilon(self, coef: float = 0.995, min_epsilon: float = 0.05) -> None:
        """
        Slowly reduce exploration.
        """
        self.epsilon = max(min_epsilon, self.epsilon * coef)

    def reset_memory(self) -> None:
        """
        Reset temporary memory between games.
        """
        self.previous_state = None
        self.previous_action = None

    def upload(self, filename: str) -> None:
        QTableDAO.save(
            filename,
            self.q_table,
            self.epsilon,
            self.alpha,
            self.gamma,
        )

    def download(self, filename: str) -> None:
        data = QTableDAO.load(filename)
        self.epsilon = data["epsilon"]
        self.alpha = data["alpha"]
        self.gamma = data["gamma"]
        self.q_table = data["q_table"]