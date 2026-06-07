import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.cubee.game_model import GameModel
    from games.cubee.player import Player


def build_state_key(game_model: "GameModel", agent: "Player") -> str:
    """
    Build a state key from the agent's point of view.

    The state contains:
    - the current turn
    - the agent's position
    - the opponent's position
    - the serialized board
    """
    agent_position = agent.position

    opponent = game_model.player2 if agent is game_model.player1 else game_model.player1
    opponent_position = opponent.position

    agent_row, agent_col = agent_position
    opponent_row, opponent_col = opponent_position
    turn = game_model.player_turn
    board = game_model.board_to_string()

    return f"{turn}|{agent_row},{agent_col}|{opponent_row},{opponent_col}|{board}"

def save_qtable(filename: str, q_table: dict, epsilon: float, alpha: float, gamma: float) -> None:
    """Save the Q-learning parameters and Q-table to a JSON file."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(
            {
                "epsilon": epsilon,
                "alpha": alpha,
                "gamma": gamma,
                "q_table": q_table,
            },
            file,
            indent=4,
        )


def load_qtable(filename: str)-> dict:
    """
    Load Q-learning parameters and Q-table from a JSON file.

    If the file does not exist, a new empty Q-table with default parameters
    is returned. If the file is invalid, the same default values are used.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        q_table = {
            state: {action: float(value) for action, value in actions.items()}
            for state, actions in data.get("q_table", {}).items()
        }

        return {
            "epsilon": float(data.get("epsilon", 0.9)),
            "alpha": float(data.get("alpha", 0.2)),
            "gamma": float(data.get("gamma", 0.9)),
            "q_table": q_table,
        }

    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "epsilon": 0.9,
            "alpha": 0.2,
            "gamma": 0.9,
            "q_table": {},
        }
