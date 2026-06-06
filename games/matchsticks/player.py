"""
Define player classes for the matches game.

This module contains:
- Player
    Base player class with a default random move.

- HumanGUI
    Human player interacting through the graphical interface.

- AI
    AI player using reinforcement learning with a state-value function.
"""

import json
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.matchsticks.game_model import GameModel


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


class HumanGUI(Player):
    """
    Human player for the Tkinter GUI.

    This class represents a human player interacting through a graphical
    interface. The player does not choose actions using the `play()` method;
    instead, actions are provided by the controller in response to button
    clicks in the GUI.
    """

    pass


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

    def _exploit(self, max_take: int) -> int:
        """
        Choose the best action using the learned value function.

        This method assumes that the AI is already attached to a game.
        That check is done in play(), because _exploit() is an internal helper.

        The AI evaluates each possible action by looking at the value of the
        state left to the opponent. It keeps the actions that lead to the lowest
        value and randomly chooses one if several actions are equally good.
        """
        state = self.game.nb

        best_value = float("inf")
        best_actions: list[int] = []

        for action in range(1, max_take + 1):
            next_state = state - action
            value = self.v_function.get(next_state, 0.0)

            if value < best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)

        return random.choice(best_actions)

    def play(self, max_take: int = 3) -> int:
        """
        Choose an action using an epsilon-greedy policy and update history.

        With probability eps, a random action is selected (exploration).
        Otherwise, _exploit() is used. The transition
        (previous_state, current_state) is stored whenever possible.

        Args:
            max_take: Maximum number of matches that can be taken.

        Returns:
            The chosen action (number of matches to take).
        """
        state = self.game.nb

        if self.previous_state is not None:
            self.history.append((self.previous_state, state))

        self.previous_state = state

        if random.random() < self.eps:
            return random.randint(1, max_take)

        return self._exploit(max_take)

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
        Update the learned value function from the last completed game.

        The AI stores transitions in history during a game. Once the game is over,
        this method goes through those transitions backwards so that the final
        result, win or lose, can progressively influence the previous states.

        For each transition, the value of the current state is moved slightly
        toward the value of the next state using a Temporal Difference update:

            V(state) <- V(state) + lr * (V(next_state) - V(state))

        After the update, history is cleared because it only represents the
        experience of one game.
        """
        for state, next_state in reversed(self.history):
            self.v_function.setdefault(state, 0.0)
            self.v_function.setdefault(next_state, 0.0)
            self.v_function[state] += self.lr * (self.v_function[next_state] - self.v_function[state])

        self.history.clear()

    def next_epsilon(self, coef: float = 0.95, min_eps: float = 0.05) -> None:
        """
        Reduce the exploration rate (epsilon).

        The value of epsilon is multiplied by a factor,
        but it will never go below the minimum value.

        Args:
            coef: Factor used to reduce epsilon.
            min_eps: Minimum allowed value for epsilon.
        """
        self.eps = max(min_eps, self.eps * coef)

    def save(self, filename: str) -> None:
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

    def load(self, filename: str) -> None:
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
