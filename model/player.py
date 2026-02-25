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
    class for a player.

    Attributes:
        name: Display name of the player.
        game: Optional reference to a game/model object.
        nb_wins: Number of wins.
        nb_loses: Number of losses.
    """

    def __init__(self, name: str, game: "GameModel | None" = None) -> None:
        """
        Initialize a player.

        Args:
            name: The player name.
            game: Optional game/model reference.
        """
        self.name = name
        self.game = game
        self.nb_wins = 0
        self.nb_loses = 0

    @property
    def nb_games(self) -> int:
        """
        Return the total number of games played.

        Returns:
            Total games = wins + losses.
        """
        return self.nb_wins + self.nb_loses

    @staticmethod
    def play(max_take: int = 3) -> int:
        """
        Choose a random action between 1 and `max_take`.

        Args:
            max_take: Maximum number of matches that can be taken this turn (>= 1).

        Returns:
            A random integer in [1, max_take].
        """
        return random.randint(1, max_take)

    def win(self) -> None:
        """Increment win counter."""
        self.nb_wins += 1

    def lose(self) -> None:
        """Increment lose counter."""
        self.nb_loses += 1

    def __str__(self) -> str:
        """Return a readable representation."""
        return (
        f"{self.name}\n"
        f"  Wins: {self.nb_wins}\n"
        f"  Losses: {self.nb_loses}\n"
        f"  Games played: {self.nb_games}"
    )


class RandomAI(Player):
    """
    Simple AI player that picks a random number of matches (1 to 3).

    The controller may limit this value when fewer than three matches remain.
    """
    pass

class AI(Player):
    def __init__(self,name,game :"GameModel | None" = None):
        
        super().__init__(name,game)
        self.eps = 0.9
        self.lr = 0.01
        self.history = []
        self.previous_state = None
        self.v_function = {"win":1.0,"lose":-1.0}

    def exploit(self, max_take: int) -> int:
        nb = self.game.nb
        best_value = -float("inf")
        best_actions = []

        for action in range(1, min(max_take, nb) + 1):
            after_me = nb - action

            if after_me == 0:
                value = self.v_function["lose"]
            else:
                worst_for_me = float("inf")
                for opp in range(1, min(max_take, after_me) + 1):
                    after_opp = after_me - opp
                    if after_opp == 0:
                        worst_for_me = min(worst_for_me, self.v_function["win"])
                    else:
                        worst_for_me = min(
                            worst_for_me,
                            self.v_function.get(after_opp, 0.0)
                        )
                value = worst_for_me

            if value > best_value:
                best_value = value
                best_actions = [action]
            elif value == best_value:
                best_actions.append(action)

        return random.choice(best_actions)
                
    def play(self, max_take:int=3):

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
        super().lose()
        if self.previous_state is not None :
            self.history.append((self.previous_state,"lose"))

        self.previous_state = None

    def train(self):
        for state,state_p in reversed(self.history):
            if state not in self.v_function: 
                self.v_function.setdefault(state,0)
            if state_p not in self.v_function: 
                self.v_function.setdefault(state_p, 0)

            self.v_function[state] += self.lr*(self.v_function[state_p]-self.v_function[state])

        self.history.clear()

    def next_epsilon(self,coef = 0.95,min_eps=0.05):
        
        self.eps = max(min_eps,self.eps*coef)
    
    def upload(self, filename: str) -> None:
        data = {
            "epsilon": self.eps,
            "lr": self.lr,
            "v_function": self.v_function
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def download(self, filename: str) -> None:
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


