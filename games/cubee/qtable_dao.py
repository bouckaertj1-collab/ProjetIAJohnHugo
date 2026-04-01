import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from games.cubee.game_model import GameModel
    from games.cubee.player import Player


def build_state_key(game_model: "GameModel", player: "Player") -> str:
    """
    Build a compact representation of a state for the Q-table.

    The state is described from the player point of view using:
    - whose turn it is
    - the player position
    - the opponent position
    - the serialized board
    """
    if game_model.player1 == player:
        my_pos = game_model.player1.position
        opponent_pos = game_model.player2.position
    else:
        my_pos = game_model.player2.position
        opponent_pos = game_model.player1.position

    my_row, my_col = my_pos
    opp_row, opp_col = opponent_pos
    turn = game_model.player_turn
    board = game_model.board_to_string()

    return f"{turn}|{my_row},{my_col}|{opp_row},{opp_col}|{board}"


def save_qtable(filename: str, q_table: dict[str, dict[str, float]], epsilon: float, alpha: float, gamma: float) -> None:
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


def load_qtable(filename: str) -> dict[str, float | dict[str, dict[str, float]]]:
    """
    Load the Q-learning parameters and Q-table from a JSON file.

    If the file does not exist or is invalid, default values are returned.
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
