"""
Define player classes for the matches game.

This module contains:
- Player
    Base abstract class representing a player.

- RandomAI
    AI player that selects moves randomly among valid moves.

- AI
    AI player using a decision algorithm (e.g., MinMax or other strategy).

- Human
    Human player interacting through the console.

- HumanGUI
    Human player interacting through the graphical interface.

"""

import json
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.matchsticks.model.game_model import GameModel


class Player:
    """
    Base class representing a player.

    Attributes:
        name: Display name of the player.
        game: Optional reference to the game model.
        nb_wins: Number of games won.
        nb_loses: Number of games lost.
    """

    def __init__(self, name: str, game: "GameModel | None" = None) -> None:
        """
        Initialize a Player instance.

        Args:
            name: Player display name.
            game: Associated game model (optional).
        """
        self.name: str = name
        self.game: "GameModel | None" = game
        self.nb_wins: int = 0
        self.nb_loses: int = 0

    @property
    def nb_games(self) -> int:
        """
        Total number of games played.

        Returns:
            Sum of wins and losses.
        """
        return self.nb_wins + self.nb_loses

    @staticmethod
    def play(max_take: int = 3) -> int:
        """
        Randomly select the number of matches to take.

        Args:
            max_take: Maximum number of matches that can be taken in one turn.

        Returns:
            Random integer in the inclusive range [1, max_take].

        Raises:
            ValueError: If max_take < 1.
        """
        if max_take < 1:
            raise ValueError("max_take must be >= 1")
        return random.randint(1, max_take)

    def win(self) -> None:
        """Record a win."""
        self.nb_wins += 1

    def lose(self) -> None:
        """Record a loss."""
        self.nb_loses += 1

    def __str__(self) -> str:
        """
        Return a readable summary of the player's statistics.

        Returns:
            Formatted player information.
        """
        return (
            f"{self.name}\n"
            f"  Wins: {self.nb_wins}\n"
            f"  Losses: {self.nb_loses}\n"
            f"  Games played: {self.nb_games}"
        )


class RandomAI(Player):
    """
    Player that relies entirely on random decisions.

    This class does not override behavior from Player; it exists mainly
    to explicitly represent a random AI agent. The actual move selection
    is handled by Player.play().

    The controller/model may further restrict the allowed move when fewer
    matches remain.
    """


class AI(Player):
    """
    Reinforcement-learning based AI player using a value function.

    The agent uses an epsilon-greedy policy to balance exploration and
    exploitation. It learns a state-value function (v_function) from
    experience and updates it after each episode.

    Attributes:
        eps: Exploration probability.
        lr: Learning rate for value updates.
        history: List of (s, s') transitions collected during an episode.
        previous_state: Previous observed state, used to build transitions.
        v_function: Estimated value of states and terminal outcomes.
    """

    def __init__(self, name: str, game: "GameModel | None" = None) -> None:
        """Initialize the AI learning parameters and value function."""
        super().__init__(name, game)
        self.eps: float = 0.9
        self.lr: float = 0.01
        self.history: list[tuple[int, int | str]] = []
        self.previous_state: int | None = None
        self.v_function: dict[int | str, float] = {"win": 1.0, "lose": -1.0}

    def exploit(self, max_take: int) -> int:
        """
        Select the best action according to the current value function.

        This method evaluates each possible action by looking at the value
        of the state that results immediately after the AI's move.
        The action leading to the lowest estimated value is selected
        (assuming the value represents the opponent's advantage).

        If multiple actions share the same best value, one is chosen randomly.

        Args:
            max_take (int): Maximum number of matches that can be taken.

        Returns:
            int: The number of matches chosen by the AI.

        Raises:
            RuntimeError: If no game is attached to the AI.
        """

        if self.game is None:
            raise RuntimeError("AI has no game attached.")

        state: int = self.game.nb
        pairing_action_value: list[tuple[int, float]] = []

        for action in range(1, max_take + 1):
            next_state: int = state - action
            self.v_function.setdefault(next_state, 0.0)
            pairing_action_value.append((action, self.v_function[next_state]))

        min_value: float = min(value for (_, value) in pairing_action_value)

        best_actions: list[int] = [
            action for (action, value) in pairing_action_value if value == min_value
        ]

        return random.choice(best_actions)

    def play(self, max_take: int = 3) -> int:
        """
        Choose an action using an epsilon-greedy policy and update history.

        With probability eps, a random action is selected (exploration).
        Otherwise, exploit() is used (exploitation). The transition
        (previous_state, current_state) is stored whenever possible.

        Args:
            max_take: Maximum number of matches that can be taken.

        Returns:
            The chosen action (number of matches to take).

        Raises:
            RuntimeError: If no game is attached to this player.
        """
        if self.game is None:
            raise RuntimeError("AI has no game attached (self.game is None).")

        state = self.game.nb

        if self.previous_state is not None:
            self.history.append((self.previous_state, state))

        self.previous_state = state

        if random.random() < self.eps:
            return random.randint(1, max_take)

        return self.exploit(max_take)

    def win(self) -> None:
        """
        Record a win and finish the current game.

        If a previous state exists, a final transition to "win" is added
        to the history. The internal state is then reset.
        """
        super().win()
        if self.previous_state is not None:
            self.history.append((self.previous_state, "win"))
        self.previous_state = None

    def lose(self) -> None:
        """
        Record a loss and finish the current game.

        If a previous state exists, a final transition to "lose" is added
        to the history. The internal state is then reset.
        """
        super().lose()
        if self.previous_state is not None:
            self.history.append((self.previous_state, "lose"))
        self.previous_state = None

    def train(self) -> None:
        """
        Update the value function using the recorded game history.

        The update is done backwards through the stored transitions
        using the rule:
            V(s) <- V(s) + lr * (V(s') - V(s))

        Side effects:
            - Modifies self.v_function
            - Clears self.history
        """
        for state, state_p in reversed(self.history):
            self.v_function.setdefault(state, 0.0)
            self.v_function.setdefault(state_p, 0.0)
            self.v_function[state] += self.lr * (self.v_function[state_p] - self.v_function[state])

        self.history.clear()

    def next_epsilon(self, coef: float = 0.95, min_eps: float = 0.05) -> None:
        """
        Reduce the exploration rate (epsilon).

        The value of epsilon is multiplied by a factor,
        but it will never go below the minimum value.

        Args:
            coef: Factor used to reduce epsilon.
            min_eps: Minimum allowed value for epsilon.

        Side effects:
            Updates self.eps.
        """
        self.eps = max(min_eps, self.eps * coef)

    def upload(self, filename: str) -> None:
        """
        Save learning parameters to a JSON file.

        Args:
            filename: Path to the output file.
        """
        data = {
            "epsilon": self.eps,
            "lr": self.lr,
            "v_function": self.v_function,
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def download(self, filename: str) -> None:
        """
        Load learning parameters from a JSON file.

        Args:
            filename: Path to the input file.
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.eps = float(data["epsilon"])
        self.lr = float(data["lr"])

        raw_v_function: dict[str, float] = data["v_function"]
        self.v_function = {}
        for k_str, v in raw_v_function.items():
            key: int | str = k_str if k_str in ("win", "lose") else int(k_str)
            self.v_function[key] = float(v)

class Human(Player):
    """
    Human player for console-based games.

    The player is asked to choose a number of matches to take via standard input.
    """

    def play(self, max_take: int = 3) -> int:
        """
        Ask the user to choose how many matches to take.

        The choice must be an integer between 1 and 3.
        The user is prompted again until a valid input is provided.

        Returns:
            int: The number of matches chosen by the player (1, 2, 3).
        """
        choice = None

        while choice not in range(1, max_take + 1):
            try:
                choice = int(input(f"{self.name}, take 1 to {max_take} matches: "))
            except ValueError:
                choice = None

            if choice not in range(1, max_take + 1):
                print(f"Invalid choice. Please enter a number between 1 and {max_take}.")

        return choice


class HumanGUI(Player):
    """
    Human player for the Tkinter GUI.

    This class represents a human player interacting through a graphical
    interface. The player does not choose actions using the `play()` method;
    instead, actions are provided by the controller in response to button
    clicks in the GUI.
    """

    pass