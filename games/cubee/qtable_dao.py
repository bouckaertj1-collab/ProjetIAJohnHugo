import json


class QTableDAO:
    @staticmethod
    def save(
        filename: str,
        q_table: dict[str, dict[str, float]],
        epsilon: float,
        alpha: float,
        gamma: float,
    ) -> None:
        """
        Save the Q-learning parameters and Q-table to a JSON file.

        Args:
            filename: Path of the JSON file.
            q_table: Q-table mapping each state to its action values.
            epsilon: Exploration rate.
            alpha: Learning rate.
            gamma: Discount factor.
        """
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

    @staticmethod
    def load(filename: str) -> dict[str, float | dict[str, dict[str, float]]]:
        """
        Load the Q-learning parameters and Q-table from a JSON file.

        If the file does not exist or is invalid, default values are returned.

        Args:
            filename: Path of the JSON file.

        Returns:
            A dictionary containing epsilon, alpha, gamma and q_table.
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