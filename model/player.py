"""
Define base player classes and simple AI players.
"""
import random
from typing import TYPE_CHECKING
import json 

if TYPE_CHECKING:
    from model.game_model import GameModel

class Player:
    """
    Base class representing a player.

    Attributes:
        name (str): Display name of the player.
        game (GameModel | None): Optional reference to the game model.
        nb_wins (int): Number of games won.
        nb_loses (int): Number of games lost.
    """
    def __init__(self, name: str, game: "GameModel | None" = None) -> None:
        """
        Initialize a Player instance.

        Args:
            name (str): Player display name.
            game (GameModel | None, optional): Associated game model.
        """
        self.name = name
        self.game = game
        self.nb_wins = 0
        self.nb_loses = 0

    @property
    def nb_games(self) -> int:
        """
        Compute the total number of games played.

        Returns:
            int: Sum of wins and losses.
        """
        return self.nb_wins + self.nb_loses

    @staticmethod
    def play(max_take: int = 3) -> int:
        """
        Randomly select the number of matches to take.

        Args:
            max_take (int, optional): Maximum number of matches
                that can be taken in one turn (must be >= 1).

        Returns:
            int: Random integer in the inclusive range [1, max_take].
        """
        return random.randint(1, max_take)

    def win(self) -> None:
        """Increment win counter of a Player instance."""
        self.nb_wins += 1

    def lose(self) -> None:
        """Increment lose counter of a Player instance."""
        self.nb_loses += 1

    def __str__(self) -> str:
        """
        Return a human-readable summary of the player's statistics.

        Returns:
            str: Formatted player information.
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

    This class does not override behavior from Player; it exists
    mainly to explicitly represent a random AI agent. The actual
    move selection is handled by Player.play().

    The controller may further restrict the allowed move when
    fewer matches remain.
    """

class AI(Player):
    """
    Reinforcement-learning based AI player.

    This agent uses an epsilon-greedy policy to balance exploration
    and exploitation. It learns a state-value function (`v_function`)
    from game experience and updates it after each episode.

    Attributes:
        eps (float): Exploration probability.
        lr (float): Learning rate for value updates.
        history (list[tuple]): Sequence of visited state transitions.
        previous_state (int | None): Last observed state.
        v_function (dict): Estimated value of states and terminal outcomes.
    """
    def __init__(self,name,game :"GameModel | None" = None):
        
        super().__init__(name,game)
        self.eps = 0.9
        self.lr = 0.01
        self.history = []
        self.previous_state = None
        self.v_function = {"win":1.0,"lose":-1.0}

    def exploit(self, max_take: int) -> int:
        """
        Select the best action using a greedy minimax strategy.

            For each possible action, the agent evaluates the resulting
            state assuming the opponent will respond optimally (i.e.,
            choose the move that minimizes this agent's outcome). The
            agent then selects the action that maximizes its guaranteed
            value. If multiple actions share the same best value, one
            is chosen uniformly at random.

        Args:
            max_take (int): Maximum number of tokens that can be taken.

        Returns:
            int: Number of tokens to take.
        """

        matches_when_ai_turn = self.game.nb

        best_score_for_ai = -float("inf")
        best_possible_actions = []

        
        for ai_move in range(1, min(max_take, matches_when_ai_turn) + 1):

            
            matches_after_ai_move = matches_when_ai_turn - ai_move

            if matches_after_ai_move == 0:
                score_for_this_move = self.v_function["lose"]

            else:
                
                worst_state_value_for_ai = float("inf")

                
                for opponent_move in range(1, min(max_take, matches_after_ai_move) + 1):

                   
                    matches_when_ai_plays_again = matches_after_ai_move - opponent_move

                   
                    if matches_when_ai_plays_again == 0:
                        state_value = self.v_function["win"]
                    else:
                        state_value = self.v_function.get(matches_when_ai_plays_again, 0.0)

                    
                    worst_state_value_for_ai = min(worst_state_value_for_ai, state_value)

                score_for_this_move = worst_state_value_for_ai

            
            if score_for_this_move > best_score_for_ai:
                best_score_for_ai = score_for_this_move
                best_possible_actions = [ai_move]
            elif score_for_this_move == best_score_for_ai:
                best_possible_actions.append(ai_move)

        return random.choice(best_possible_actions)
    def play(self,max_take:int=3):
        """
        Chooses an action according to an epsilon-greedy policy and updates history.

        With probability `eps`, a random action is selected (exploration).
        Otherwise, the `exploit` method is called to choose the best known action
        (exploitation). The previous and current states are recorded in history
        to support learning.

        Args:
            max_take (int, optional): Maximum number of tokens that can be taken.
                                  Defaults to 3.

        Returns:
            int: The chosen action (number of tokens to take).

        Side effects:
            - Updates `self.history` with the tuple (previous_state, current_state)
                if a previous state exists.
            - Updates `self.previous_state` to the current state.
        """
        state = self.game.nb

        if self.previous_state is not None:
            self.history.append((self.previous_state,state))

        self.previous_state = state

        if random.random() < self.eps:
            action = random.randint(1, max_take)
        else:
            action = self.exploit(max_take)

        return action
    
    def win(self):
        super().win()
        if self.previous_state is not None :
            self.history.append((self.previous_state,"win"))
        
        self.previous_state = None

    def lose(self):
        """
        Record a loss and finalize the current episode.

        Adds a terminal transition to the history if a previous
        state exists, then resets the internal state tracker.
    """
        super().lose()
        if self.previous_state is not None :
            self.history.append((self.previous_state,"lose"))

        self.previous_state = None

    def train(self):
        """
        Update the value function using the recorded history.

        The method performs a backward update over the stored
        state transitions using a temporal-difference style rule.
        After updating, the history buffer is cleared.

        Side Effects:
            - Modifies `self.v_function`
            - Clears `self.history`
        """
        for state,state_p in reversed(self.history):
            if state not in self.v_function: 
                self.v_function.setdefault(state,0)
            if state_p not in self.v_function: 
                self.v_function.setdefault(state_p, 0)

            self.v_function[state] += self.lr*(self.v_function[state_p]-self.v_function[state])

        self.history.clear()

    def next_epsilon(self,coef = 0.95,min_eps=0.05):
        """
        Decay the exploration rate.

        Args:
            coef (float, optional): Multiplicative decay factor.
            min_eps (float, optional): Minimum allowed epsilon value.

        Side Effects:
            Updates `self.eps`.
    """
        
        self.eps = max(min_eps,self.eps*coef)
    

    def upload(self, filename: str) -> None:
        """
        Save the learning parameters to a JSON file.

        Args:
            filename (str): Path to the output file.

        Side Effects:
            Writes data to disk.
        """
        data = {
            "epsilon": self.eps,
            "lr": self.lr,
            "v_function": self.v_function
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def download(self, filename: str) -> None:
        """
        Load learning parameters from a JSON file.

        Args:
            filename (str): Path to the input file.

        Side Effects:
            Updates epsilon, learning rate, and value function.
        """
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.eps = data["epsilon"]
        self.lr = data["lr"]
        v_function_str = data['v_function']

        self.v_function = {}
        for k_str, v in v_function_str.items():
            if k_str in ['win', 'lose']:
                k = k_str
            else:
                k = int(k_str)
            self.v_function[k] = v


